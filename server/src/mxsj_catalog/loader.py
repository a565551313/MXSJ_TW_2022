"""Loader implementation for MXSJ review catalog."""

import csv
import hashlib
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

# Reverse lookup from file path to short id
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
    # Check if raw is already a manifest filename
    if raw in FILE_TO_SHORT_ID:
        return raw
    # Check if stripping .csv matches a manifest filename
    if not raw.endswith(".csv") and (raw + ".csv") in FILE_TO_SHORT_ID:
        return raw + ".csv"
    # Check if base name matches
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
        # Fallback to string for unhandled types
        return str(val)


def load_raw_dataset(
    file_rel_path: str,
    meta: dict[str, Any],
    base_dir: Path,
) -> Dataset:
    """Load, validate, and index a single CSV dataset according to manifest."""
    csv_path = base_dir / file_rel_path
    if not csv_path.is_file():
        raise CatalogIntegrityError(f"Missing CSV file: {csv_path}")

    # Read bytes and verify integrity
    with open(csv_path, "rb") as f:
        data = f.read()

    expected_bytes = meta.get("bytes")
    if expected_bytes is not None and len(data) != expected_bytes:
        raise CatalogIntegrityError(
            f"File size mismatch for {file_rel_path}: expected {expected_bytes}, got {len(data)}"
        )

    expected_sha256 = meta.get("sha256")
    if expected_sha256 is not None:
        actual_sha256 = hashlib.sha256(data).hexdigest()
        if actual_sha256 != expected_sha256:
            raise CatalogIntegrityError(
                f"SHA256 mismatch for {file_rel_path}: expected {expected_sha256}, got {actual_sha256}"
            )

    columns_meta = meta.get("columns", [])
    col_defs = tuple(ColumnDef(name=c["name"], type=c["type"]) for c in columns_meta)
    col_names = [c.name for c in col_defs]
    col_types = {c.name: c.type for c in col_defs}
    primary_keys = tuple(meta.get("primary_key", []))

    # Read CSV
    text_content = data.decode("utf-8")
    lines = text_content.splitlines()
    reader = csv.reader(lines)

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
                if pk_col not in row_dict:
                    raise CatalogKeyError(
                        f"Primary key column '{pk_col}' missing from row {row_idx} in {file_rel_path}"
                    )
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
    if expected_rows is not None and len(records) != expected_rows:
        raise CatalogIntegrityError(
            f"Row count mismatch in {file_rel_path}: expected {expected_rows}, got {len(records)}"
        )

    short_id = FILE_TO_SHORT_ID.get(file_rel_path, Path(file_rel_path).stem)
    schema = DatasetSchema(
        id=short_id,
        filename=file_rel_path,
        rows=len(records),
        primary_key=primary_keys,
        columns=col_defs,
        notes=meta.get("notes", ""),
        source_entry=meta.get("source_entry"),
        source_table=meta.get("source_table"),
        csv_format=meta.get("csv_format", ""),
        schema_document=meta.get("schema_document", ""),
    )

    return Dataset(
        schema=schema,
        records=tuple(records),
        index_by_pk=MappingProxyType(pk_map),
    )
