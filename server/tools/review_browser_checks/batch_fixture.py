"""Independent reader for the first review CSV batch (batch_001).

This module belongs to the independent acceptance/regression tooling (Agent J).
It deliberately does **not** import ``server/tools/export_review_csv.py`` or any
Agent H loader code, so that the numbers asserted by the acceptance suite are
recomputed from the committed artefacts instead of being echoed back by the
producer that wrote them.

Only the Python standard library is used.

Data contract read from the artefacts themselves:

* ``manifest.json``      - column names/types, rows, bytes, sha256, primary keys
* core CSVs              - UTF-8 without BOM, all fields quoted, LF newlines
* ``maps_npcs/*.csv``    - UTF-8 without BOM, minimal quoting, CRLF (E staging)
* ``quarantine.jsonl``   - typed JSON envelope: ``{"bytes_hex": ...}``,
  ``{"tuple": [...]}``, ``{"list": [...]}``, ``{"dict": [[k, v], ...]}``
  (re-implemented here from the documented format; the producer's own
  ``restore()`` is intentionally not reused).
"""
from __future__ import annotations

import csv
import hashlib
import io
import json
import shutil
from pathlib import Path

# Files whose declared rows/bytes/sha256 the acceptance suite recomputes.
CORE_CSVS = (
    'items.csv',
    'pets.csv',
    'pet_aptitudes.csv',
    'pet_aptitude_missing.csv',
    'pet_skills.csv',
    'pet_skill_candidates.csv',
    'pet_required_skills.csv',
    'pet_skill_name_matches.csv',
    'pet_skill_overwrites.csv',
)
MAP_NPC_CSVS = (
    'maps_npcs/mapdata_scene_dictionary.csv',
    'maps_npcs/mapdata_parent_scene.csv',
    'maps_npcs/sceneid2name_minimap_scenes.csv',
    'maps_npcs/npcname2realnamedata_alias_to_realname.csv',
    'maps_npcs/npcposdata_records.csv',
    'maps_npcs/minimapnpcpos_pos_records.csv',
    'maps_npcs/minimapnpcpos_wenzi_entries.csv',
    'maps_npcs/npc_2601_vs_2804_agreement.csv',
)

# Frozen expectations for the fixed review inputs. These come from
# BATCH_001.md / AGENT_G_CONSOLIDATION.md / validation.json, not from whatever
# the artefacts happen to contain: a failing value here is a finding.
FIXED_EXPECTATIONS = {
    'items_rows': 6851,
    'pets_rows': 135,
    'pet_aptitudes_rows': 131,
    'pet_skills_rows': 579,
    'pet_skill_candidates_rows': 458,
    'pet_required_skills_rows': 26,
    'referenced_skill_names': 143,
    'pet_skill_name_match_rows': 145,
    'single_id_skill_names': 141,
    'ambiguous_skill_name_matches': {
        '高級命中': [229, 255],
        '終級命中': [329, 355],
    },
    'skill_overwrite_rows': 9,
    'quarantined_records': 4,
    'missing_aptitude_rows': 3,
    'missing_aptitude_ids': [3010, 4021, 4022],
    'quarantined_keys': [
        {'entry_index': 1945, 'record_key': 72548},
        {'entry_index': 2954, 'record_key': 2800},
        {'entry_index': 3205, 'record_key': 719},
        {'entry_index': 3205, 'record_key': 4406},
    ],
    'map_npc_rows': {
        'maps_npcs/mapdata_scene_dictionary.csv': 104,
        'maps_npcs/mapdata_parent_scene.csv': 6,
        'maps_npcs/sceneid2name_minimap_scenes.csv': 57,
        'maps_npcs/npcname2realnamedata_alias_to_realname.csv': 55,
        'maps_npcs/npcposdata_records.csv': 1335,
        'maps_npcs/minimapnpcpos_pos_records.csv': 1344,
        'maps_npcs/minimapnpcpos_wenzi_entries.csv': 287,
        'maps_npcs/npc_2601_vs_2804_agreement.csv': 677,
    },
    'zero_npcid_records': {'npcposdata': 632, 'minimapnpcpos_pos': 631},
    'source_entries': {
        'items.csv': (1945,),
        'pets.csv': (2027,),
        'pet_aptitudes.csv': (2954,),
        'pet_aptitude_missing.csv': (2954,),
        'pet_skills.csv': (3205,),
        'pet_skill_candidates.csv': (2027,),
        'pet_required_skills.csv': (2027,),
        'pet_skill_name_matches.csv': (3205,),
        'pet_skill_overwrites.csv': (3205,),
        'maps_npcs/mapdata_scene_dictionary.csv': (1301,),
        'maps_npcs/mapdata_parent_scene.csv': (1301,),
        'maps_npcs/sceneid2name_minimap_scenes.csv': (400,),
        'maps_npcs/npcname2realnamedata_alias_to_realname.csv': (1799,),
        'maps_npcs/npcposdata_records.csv': (2601,),
        'maps_npcs/minimapnpcpos_pos_records.csv': (2804,),
        'maps_npcs/minimapnpcpos_wenzi_entries.csv': (2804,),
        'maps_npcs/npc_2601_vs_2804_agreement.csv': (2601, 2804),
    },
    # Text that must survive unchanged (traditional forms, no S/T conversion).
    'required_traditional_strings': (
        '終級命中', '高級命中', '時空石', '天魔返生術', '地魔返生術', '裝備店',
    ),
    # Strings that would only appear after a simplified rewrite of the source.
    'forbidden_simplified_strings': (
        '宠物', '资质', '技能书', '装备店', '时空石', '高级命中', '终极命中',
    ),
}


def repo_root() -> Path:
    return Path(__file__).resolve().parents[3]


def default_batch_dir() -> Path:
    return repo_root() / 'server/docs/csv_checks/batch_001'


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(Path(path).read_bytes())


class BatchError(AssertionError):
    """Raised when an artefact contradicts the documented review contract."""


class TypedJson:
    """Decoder for the documented typed-JSON evidence envelope."""

    @staticmethod
    def decode(value):
        if isinstance(value, dict):
            keys = set(value)
            if keys == {'bytes_hex'}:
                return bytes.fromhex(value['bytes_hex'])
            if keys == {'tuple'}:
                return tuple(TypedJson.decode(v) for v in value['tuple'])
            if keys == {'list'}:
                return [TypedJson.decode(v) for v in value['list']]
            if keys == {'dict'}:
                pairs = [(TypedJson.decode(k), TypedJson.decode(v)) for k, v in value['dict']]
                decoded = dict(pairs)
                if len(decoded) != len(pairs):
                    raise BatchError('typed JSON dict envelope contains a duplicate key')
                return decoded
            raise BatchError(f'unknown typed JSON envelope: {sorted(keys)}')
        return value

    @staticmethod
    def text(value) -> str:
        if not isinstance(value, bytes):
            raise BatchError('expected CP950 byte string in typed evidence')
        return value.decode('cp950')


class Batch:
    """Read-only view of a review CSV batch directory."""

    def __init__(self, root: Path | str | None = None):
        self.root = Path(root) if root is not None else default_batch_dir()
        self._raw: dict[str, bytes] = {}
        self._rows: dict[str, list[dict]] = {}

    # -- raw access -----------------------------------------------------
    def read_bytes(self, name: str) -> bytes:
        if name not in self._raw:
            self._raw[name] = (self.root / name).read_bytes()
        return self._raw[name]

    def manifest(self) -> dict:
        return json.loads(self.read_bytes('manifest.json').decode('utf-8'))

    def validation(self) -> dict:
        return json.loads(self.read_bytes('validation.json').decode('utf-8'))

    def quarantine(self) -> list[dict]:
        return [json.loads(line) for line in
                self.read_bytes('quarantine.jsonl').decode('utf-8').splitlines() if line.strip()]

    def overwrite_evidence(self) -> list[dict]:
        return [json.loads(line) for line in
                self.read_bytes('overwrite_evidence.jsonl').decode('utf-8').splitlines() if line.strip()]

    def file_names(self) -> set[str]:
        return {p.relative_to(self.root).as_posix() for p in self.root.rglob('*') if p.is_file()}

    # -- typed CSV access ----------------------------------------------
    def csv_text(self, name: str) -> str:
        data = self.read_bytes(name)
        if data.startswith(b'\xef\xbb\xbf'):
            raise BatchError(f'{name}: unexpected UTF-8 BOM')
        try:
            return data.decode('utf-8')
        except UnicodeDecodeError as exc:
            raise BatchError(f'{name}: not UTF-8 ({exc})') from exc

    def header(self, name: str) -> list[str]:
        text = self.csv_text(name)
        first = text.split('\n', 1)[0].replace('\r', '')
        return next(csv.reader(io.StringIO(first)))

    def rows(self, name: str) -> list[dict]:
        if name not in self._rows:
            text = self.csv_text(name)
            self._rows[name] = list(csv.DictReader(io.StringIO(text, newline='')))
        return self._rows[name]

    def columns(self, name: str) -> list[dict]:
        return self.manifest()['files'][name]['columns']

    def typed(self, name: str) -> list[dict]:
        """Rows converted using the column types declared in the manifest."""
        per_column = {c['name']: c['type'] for c in self.columns(name)}
        out = []
        for row in self.rows(name):
            if set(row) != set(per_column):
                raise BatchError(f'{name}: row keys do not match manifest columns')
            converted = {}
            for key, kind in per_column.items():
                converted[key] = self._convert(name, key, kind, row[key])
            out.append(converted)
        return out

    @staticmethod
    def _convert(name: str, column: str, kind: str, value: str):
        if kind == 'str':
            return value
        if kind == 'int':
            try:
                return int(value)
            except ValueError as exc:
                raise BatchError(f'{name}.{column}: {value!r} is not an int') from exc
        if kind == 'bool':
            if value not in ('true', 'false'):
                raise BatchError(f'{name}.{column}: {value!r} is not a true/false literal')
            return value == 'true'
        if kind == 'int_or_empty':
            if value == '':
                return None
            try:
                return int(value)
            except ValueError as exc:
                raise BatchError(f'{name}.{column}: {value!r} is not int_or_empty') from exc
        raise BatchError(f'{name}.{column}: unsupported manifest type {kind!r}')

    # -- convenience ----------------------------------------------------
    def ids(self, name: str, column: str) -> list:
        return [row[column] for row in self.typed(name)]


def write_temp_batch(destination: Path, source: Path | None = None, *,
                     mutate: dict[str, bytes] | None = None) -> Path:
    """Copy a batch into a scratch directory (never mutate the committed one).

    ``mutate`` maps a relative file name to replacement bytes and is applied
    after copying, so abnormal-input tests work on throwaway copies only.
    """
    source = Path(source) if source is not None else default_batch_dir()
    destination = Path(destination)
    if destination.exists():
        if any(destination.iterdir()):
            raise BatchError(f'refusing to write into a non-empty directory: {destination}')
    else:
        destination.mkdir(parents=True)
    shutil.copytree(source, destination, dirs_exist_ok=True)
    for name, data in (mutate or {}).items():
        target = destination / name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(data)
    return destination
