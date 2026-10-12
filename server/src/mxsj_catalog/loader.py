"""Loader implementation for MXSJ review catalog."""

import csv
import hashlib
import io
import json
from pathlib import Path
from types import MappingProxyType
from typing import Any, Mapping

from .errors import (
    CatalogIntegrityError,
    CatalogKeyError,
    CatalogSchemaError,
    CatalogValueError,
)
from .models import (
    ColumnDef,
    Dataset,
    DatasetSchema,
    OverwriteEvidence,
    QuarantineRecord,
)

REQUIRED_CSV_FILES: frozenset[str] = frozenset({
    "items.csv",
    "pets.csv",
    "pet_skill_candidates.csv",
    "pet_required_skills.csv",
    "pet_aptitudes.csv",
    "pet_aptitude_missing.csv",
    "pet_skills.csv",
    "pet_skill_overwrites.csv",
    "pet_skill_name_matches.csv",
    "maps_npcs/mapdata_parent_scene.csv",
    "maps_npcs/mapdata_scene_dictionary.csv",
    "maps_npcs/minimapnpcpos_pos_records.csv",
    "maps_npcs/minimapnpcpos_wenzi_entries.csv",
    "maps_npcs/npc_2601_vs_2804_agreement.csv",
    "maps_npcs/npcname2realnamedata_alias_to_realname.csv",
    "maps_npcs/npcposdata_records.csv",
    "maps_npcs/sceneid2name_minimap_scenes.csv",
})

REQUIRED_EVIDENCE_FILES: frozenset[str] = frozenset({
    "quarantine.jsonl",
    "overwrite_evidence.jsonl",
    "validation.json",
    "maps_npcs/provenance.json",
})

ALL_REQUIRED_FILES: frozenset[str] = REQUIRED_CSV_FILES | REQUIRED_EVIDENCE_FILES

SUPPORTED_COLUMN_TYPES: frozenset[str] = frozenset({
    "int",
    "int_or_empty",
    "bool",
    "str",
})

SHORT_NAME_MAP: dict[str, str] = {
    "items": "items.csv",
    "pets": "pets.csv",
    "pet_skill_candidates": "pet_skill_candidates.csv",
    "pet_required_skills": "pet_required_skills.csv",
    "pet_aptitudes": "pet_aptitudes.csv",
    "pet_aptitude_missing": "pet_aptitude_missing.csv",
    "pet_skills": "pet_skills.csv",
    "pet_skill_overwrites": "pet_skill_overwrites.csv",
    "pet_skill_name_matches": "pet_skill_name_matches.csv",
    "mapdata_parent_scene": "maps_npcs/mapdata_parent_scene.csv",
    "mapdata_scene_dictionary": "maps_npcs/mapdata_scene_dictionary.csv",
    "minimapnpcpos_pos_records": "maps_npcs/minimapnpcpos_pos_records.csv",
    "minimapnpcpos_wenzi_entries": "maps_npcs/minimapnpcpos_wenzi_entries.csv",
    "npc_2601_vs_2804_agreement": "maps_npcs/npc_2601_vs_2804_agreement.csv",
    "npcname2realnamedata_alias_to_realname": "maps_npcs/npcname2realnamedata_alias_to_realname.csv",
    "npcposdata_records": "maps_npcs/npcposdata_records.csv",
    "sceneid2name_minimap_scenes": "maps_npcs/sceneid2name_minimap_scenes.csv",
}

FILE_TO_SHORT_ID: dict[str, str] = {v: k for k, v in SHORT_NAME_MAP.items()}


def normalize_dataset_id(dataset_id: str) -> str:
    """Normalize user-provided dataset identifier to manifest file path."""
    raw = dataset_id.strip()
    if raw in SHORT_NAME_MAP:
        return SHORT_NAME_MAP[raw]
    if raw.endswith(".csv"):
        base = raw[:-4]
        if base in SHORT_NAME_MAP:
            return SHORT_NAME_MAP[base]
    if raw in FILE_TO_SHORT_ID:
        return raw
    if not raw.endswith(".csv") and (raw + ".csv") in FILE_TO_SHORT_ID:
        return raw + ".csv"
    base_name = Path(raw).name
    if base_name in SHORT_NAME_MAP:
        return SHORT_NAME_MAP[base_name]
    if base_name.endswith(".csv") and base_name[:-4] in SHORT_NAME_MAP:
        return SHORT_NAME_MAP[base_name[:-4]]
    return raw


def _freeze_dict(d: Any) -> Any:
    """Recursively freeze dictionaries and lists to immutable structures."""
    if isinstance(d, dict):
        return MappingProxyType({k: _freeze_dict(v) for k, v in d.items()})
    elif isinstance(d, list):
        return tuple(_freeze_dict(x) for x in d)
    return d


def convert_value(val: str, col_type: str, col_name: str, row_idx: int) -> Any:
    """Strictly convert string value to designated column type."""
    if col_type == "int":
        try:
            return int(val.strip())
        except (ValueError, TypeError) as e:
            raise CatalogValueError(
                f"Row {row_idx}: Column '{col_name}' expects int, got {val!r}"
            ) from e
    elif col_type == "int_or_empty":
        if val is None or val == "":
            return None
        try:
            return int(val.strip())
        except (ValueError, TypeError) as e:
            raise CatalogValueError(
                f"Row {row_idx}: Column '{col_name}' expects int_or_empty, got {val!r}"
            ) from e
    elif col_type == "bool":
        stripped = val.strip().lower()
        if stripped == "true":
            return True
        elif stripped == "false":
            return False
        else:
            raise CatalogValueError(
                f"Row {row_idx}: Column '{col_name}' expects bool (true/false), got {val!r}"
            )
    elif col_type == "str":
        return str(val)
    else:
        raise CatalogValueError(
            f"Row {row_idx}: Unsupported column type '{col_type}' for column '{col_name}'"
        )


def verify_file_integrity(file_rel_path: str, meta: dict[str, Any], base_dir: Path) -> bytes:
    """Verify file existence, path containment, byte length, and SHA-256 hash."""
    resolved_base = base_dir.resolve()
    target_path = (base_dir / file_rel_path).resolve()

    try:
        target_path.relative_to(resolved_base)
    except ValueError:
        raise CatalogIntegrityError(
            f"Path traversal detected: '{file_rel_path}' is outside batch directory"
        )

    if not target_path.is_file():
        raise CatalogIntegrityError(f"Missing required file: {file_rel_path}")

    data = target_path.read_bytes()

    expected_bytes = meta.get("bytes")
    if expected_bytes is None:
        raise CatalogIntegrityError(f"Missing 'bytes' specification in manifest for {file_rel_path}")
    if len(data) != expected_bytes:
        raise CatalogIntegrityError(
            f"File size mismatch for {file_rel_path}: expected {expected_bytes}, got {len(data)}"
        )

    expected_sha256 = meta.get("sha256")
    if expected_sha256 is None:
        raise CatalogIntegrityError(f"Missing 'sha256' specification in manifest for {file_rel_path}")
    actual_sha256 = hashlib.sha256(data).hexdigest()
    if actual_sha256 != expected_sha256:
        raise CatalogIntegrityError(
            f"SHA256 mismatch for {file_rel_path}: expected {expected_sha256}, got {actual_sha256}"
        )

    return data


def load_raw_dataset(
    file_rel_path: str,
    meta: dict[str, Any],
    base_dir: Path,
) -> Dataset:
    """Load, validate, and index a single CSV dataset according to manifest."""
    # Verify file integrity and path containment
    data = verify_file_integrity(file_rel_path, meta, base_dir)

    columns_meta = meta.get("columns")
    if columns_meta is None or not isinstance(columns_meta, list):
        raise CatalogSchemaError(f"Missing or invalid 'columns' metadata for {file_rel_path}")

    # Validate column types
    for c in columns_meta:
        ctype = c.get("type")
        cname = c.get("name")
        if not cname:
            raise CatalogSchemaError(f"Unnamed column in {file_rel_path}")
        if ctype not in SUPPORTED_COLUMN_TYPES:
            raise CatalogSchemaError(
                f"Unsupported column type '{ctype}' for column '{cname}' in {file_rel_path}"
            )

    col_defs = tuple(ColumnDef(name=c["name"], type=c["type"]) for c in columns_meta)
    col_names = [c.name for c in col_defs]
    col_types = {c.name: c.type for c in col_defs}

    raw_pk = meta.get("primary_key")
    if raw_pk is None or not isinstance(raw_pk, list):
        raise CatalogSchemaError(f"Missing or invalid 'primary_key' for {file_rel_path}")

    # Check all primary_key columns exist in columns
    for pk_col in raw_pk:
        if pk_col not in col_types:
            raise CatalogSchemaError(
                f"Primary key column '{pk_col}' not found in declared columns of {file_rel_path}"
            )

    primary_keys = tuple(raw_pk)

    # Read CSV using io.StringIO to preserve multiline fields (CR, LF, CRLF inside quotes)
    text_content = data.decode("utf-8")
    reader = csv.reader(io.StringIO(text_content))

    header = next(reader, None)
    if header is None:
        raise CatalogSchemaError(f"Empty CSV file: {file_rel_path}")

    if header != col_names:
        raise CatalogSchemaError(
            f"CSV header mismatch in {file_rel_path}: expected {col_names}, got {header}"
        )

    records: list[Mapping[str, Any]] = []
    pk_map: dict[str, Mapping[str, Any]] = {}

    for row_idx, row in enumerate(reader, start=1):
        if len(row) != len(col_names):
            raise CatalogSchemaError(
                f"Row {row_idx} column count mismatch in {file_rel_path}: expected {len(col_names)}, got {len(row)}"
            )

        row_dict: dict[str, Any] = {}
        for cname, raw_val in zip(col_names, row):
            ctype = col_types[cname]
            row_dict[cname] = convert_value(raw_val, ctype, cname, row_idx)

        # Compute composite primary key string
        if primary_keys:
            pk_values = []
            for pk_col in primary_keys:
                val = row_dict[pk_col]
                pk_values.append(str(val) if val is not None else "")
            pk_str = ":".join(pk_values)
        else:
            pk_str = str(row_idx)

        if pk_str in pk_map:
            raise CatalogKeyError(
                f"Duplicate primary key {pk_str!r} at row {row_idx} in {file_rel_path}"
            )

        row_dict["_pk"] = pk_str
        frozen_row = MappingProxyType(row_dict)
        records.append(frozen_row)
        pk_map[pk_str] = frozen_row

    expected_rows = meta.get("rows")
    if expected_rows is None or len(records) != expected_rows:
        raise CatalogIntegrityError(
            f"Row count mismatch in {file_rel_path}: expected {expected_rows}, got {len(records)}"
        )

    short_id = FILE_TO_SHORT_ID.get(file_rel_path, Path(file_rel_path).stem)

    raw_source_entry = meta.get("source_entry")
    if isinstance(raw_source_entry, list):
        source_entry = tuple(raw_source_entry)
    else:
        source_entry = raw_source_entry

    schema = DatasetSchema(
        id=short_id,
        filename=file_rel_path,
        rows=len(records),
        primary_key=primary_keys,
        columns=col_defs,
        notes=meta.get("notes", ""),
        source_entry=source_entry,
        source_table=meta.get("source_table"),
        csv_format=meta.get("csv_format", ""),
        schema_document=meta.get("schema_document", ""),
    )

    return Dataset(
        schema=schema,
        records=tuple(records),
        index_by_pk=MappingProxyType(pk_map),
    )
