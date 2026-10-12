"""Review catalog management and query interface."""

import json
from pathlib import Path
from types import MappingProxyType
from typing import Any, Mapping

from .errors import (
    CatalogIntegrityError,
    DatasetNotFoundError,
    RecordNotFoundError,
)
from .loader import (
    FILE_TO_SHORT_ID,
    SHORT_NAME_MAP,
    _freeze_dict,
    load_raw_dataset,
    normalize_dataset_id,
)
from .models import (
    Dataset,
    DatasetSchema,
    OverwriteEvidence,
    QuarantineRecord,
)


def _to_plain_data(obj: Any) -> Any:
    """Recursively convert mappingproxy and tuples to plain dicts and lists."""
    if isinstance(obj, (dict, MappingProxyType)):
        return {k: _to_plain_data(v) for k, v in obj.items()}
    elif isinstance(obj, (list, tuple)):
        return [_to_plain_data(x) for x in obj]
    return obj


class ReviewCatalog:
    """Read-only catalog for batch review data."""

    def __init__(
        self,
        base_dir: Path,
        manifest: Mapping[str, Any],
        validation: Mapping[str, Any],
        provenance: Mapping[str, Any],
        datasets: dict[str, Dataset],
        quarantine: tuple[QuarantineRecord, ...],
        overwrites: tuple[OverwriteEvidence, ...],
    ) -> None:
        self._base_dir = base_dir
        self._manifest = manifest
        self._validation = validation
        self._provenance = provenance
        self._datasets = datasets
        self._quarantine = quarantine
        self._overwrites = overwrites

    @classmethod
    def load(cls, base_dir: str | Path | None = None) -> "ReviewCatalog":
        """Load and validate all catalog files according to manifest."""
        if base_dir is None:
            # Default to repo standard location
            candidate = Path(__file__).resolve().parent.parent.parent / "docs" / "csv_checks" / "batch_001"
            if not candidate.is_dir():
                candidate = Path("server/docs/csv_checks/batch_001").resolve()
            base_dir = candidate
        else:
            base_dir = Path(base_dir).resolve()

        manifest_path = base_dir / "manifest.json"
        if not manifest_path.is_file():
            raise CatalogIntegrityError(f"Missing manifest file: {manifest_path}")

        with open(manifest_path, "r", encoding="utf-8") as f:
            manifest_data = json.load(f)

        files_meta = manifest_data.get("files", {})
        datasets: dict[str, Dataset] = {}

        # 1. Load CSV datasets
        for rel_path, meta in files_meta.items():
            if rel_path.endswith(".csv"):
                dataset = load_raw_dataset(rel_path, meta, base_dir)
                short_id = dataset.schema.id
                datasets[short_id] = dataset
                # Also index by relative file path for convenience
                datasets[rel_path] = dataset

        # 2. Load quarantine.jsonl
        quarantine_list: list[QuarantineRecord] = []
        quarantine_path = base_dir / "quarantine.jsonl"
        if quarantine_path.is_file():
            with open(quarantine_path, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    item = json.loads(line)
                    quarantine_list.append(
                        QuarantineRecord(
                            entry_index=item["entry_index"],
                            table=item["table"],
                            record_key=item["record_key"],
                            reasons=tuple(item["reasons"]),
                            native_verified=item.get("native_verified", False),
                            value_under_applied_profile=_freeze_dict(
                                item.get("value_under_applied_profile", {})
                            ),
                        )
                    )

        # 3. Load overwrite_evidence.jsonl
        overwrites_list: list[OverwriteEvidence] = []
        overwrites_path = base_dir / "overwrite_evidence.jsonl"
        if overwrites_path.is_file():
            with open(overwrites_path, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    item = json.loads(line)
                    overwrites_list.append(
                        OverwriteEvidence(
                            order=item["order"],
                            code_offset=item["code_offset"],
                            entry_index=item["entry_index"],
                            table=item["table"],
                            key=item["key"],
                            old_value=_freeze_dict(item.get("old_value", {})),
                            new_value=_freeze_dict(item.get("new_value", {})),
                        )
                    )

        # 4. Load validation.json
        validation_path = base_dir / "validation.json"
        validation_data: dict[str, Any] = {}
        if validation_path.is_file():
            with open(validation_path, "r", encoding="utf-8") as f:
                validation_data = json.load(f)

        # 5. Load maps_npcs/provenance.json
        provenance_path = base_dir / "maps_npcs" / "provenance.json"
        provenance_data: dict[str, Any] = {}
        if provenance_path.is_file():
            with open(provenance_path, "r", encoding="utf-8") as f:
                provenance_data = json.load(f)

        return cls(
            base_dir=base_dir,
            manifest=MappingProxyType(manifest_data),
            validation=MappingProxyType(validation_data),
            provenance=MappingProxyType(provenance_data),
            datasets=datasets,
            quarantine=tuple(quarantine_list),
            overwrites=tuple(overwrites_list),
        )

    def list_datasets(self) -> list[dict[str, Any]]:
        """List metadata for all distinct datasets."""
        res: list[dict[str, Any]] = []
        seen = set()
        for short_id, rel_path in SHORT_NAME_MAP.items():
            if short_id in self._datasets:
                ds = self._datasets[short_id]
                seen.add(short_id)
                res.append(
                    {
                        "id": ds.schema.id,
                        "filename": ds.schema.filename,
                        "rows": ds.schema.rows,
                        "primary_key": list(ds.schema.primary_key),
                        "notes": ds.schema.notes,
                        "source_entry": ds.schema.source_entry,
                        "source_table": ds.schema.source_table,
                        "columns": [
                            {"name": c.name, "type": c.type} for c in ds.schema.columns
                        ],
                    }
                )
        return res

    def get_dataset(self, dataset_id: str) -> Dataset:
        """Fetch dataset by ID or raise DatasetNotFoundError."""
        normalized = normalize_dataset_id(dataset_id)
        if normalized in self._datasets:
            return self._datasets[normalized]
        if dataset_id in self._datasets:
            return self._datasets[dataset_id]
        raise DatasetNotFoundError(f"Dataset '{dataset_id}' does not exist.")

    def get_record(self, dataset_id: str, pk: str) -> dict[str, Any] | None:
        """Fetch single record by primary key."""
        dataset = self.get_dataset(dataset_id)
        row = dataset.get_by_pk(pk)
        if row is None:
            return None
        # Return a copy to guarantee caller immutability
        return dict(row)

    def query_records(
        self,
        dataset_id: str,
        offset: int = 0,
        limit: int = 50,
        q: str | None = None,
        filters: dict[str, Any] | None = None,
        sort_by: str | None = None,
        order: str = "asc",
    ) -> tuple[list[dict[str, Any]], int]:
        """Query, filter, search, sort, and paginate dataset records."""
        dataset = self.get_dataset(dataset_id)

        if offset < 0:
            raise ValueError(f"Offset must be >= 0, got {offset}")
        if limit < 1 or limit > 500:
            raise ValueError(f"Limit must be between 1 and 500, got {limit}")

        col_types = {c.name: c.type for c in dataset.schema.columns}
        col_types["_pk"] = "str"

        # Validate sort_by
        if sort_by is not None and sort_by not in col_types:
            raise ValueError(
                f"Invalid sort column '{sort_by}'. Available columns: {list(col_types.keys())}"
            )

        # Validate and normalize filters
        normalized_filters: dict[str, Any] = {}
        if filters:
            for k, val in filters.items():
                if k not in col_types:
                    raise ValueError(
                        f"Unknown filter column '{k}'. Available columns: {list(col_types.keys())}"
                    )
                target_type = col_types[k]
                if target_type == "int":
                    try:
                        normalized_filters[k] = int(val)
                    except (ValueError, TypeError) as e:
                        raise ValueError(
                            f"Filter value for '{k}' must be int, got {val!r}"
                        ) from e
                elif target_type == "int_or_empty":
                    if val is None or val == "" or str(val).lower() == "null":
                        normalized_filters[k] = None
                    else:
                        try:
                            normalized_filters[k] = int(val)
                        except (ValueError, TypeError) as e:
                            raise ValueError(
                                f"Filter value for '{k}' must be int or null, got {val!r}"
                            ) from e
                elif target_type == "bool":
                    s = str(val).strip().lower()
                    if s == "true":
                        normalized_filters[k] = True
                    elif s == "false":
                        normalized_filters[k] = False
                    else:
                        raise ValueError(
                            f"Filter value for '{k}' must be bool ('true'/'false'), got {val!r}"
                        )
                else:
                    normalized_filters[k] = str(val)

        # Pre-process search query q
        q_clean = q.strip().lower() if q is not None and q.strip() else None

        filtered: list[Mapping[str, Any]] = []
        for record in dataset.records:
            # Check filters
            match = True
            for k, expected_v in normalized_filters.items():
                if record.get(k) != expected_v:
                    match = False
                    break
            if not match:
                continue

            # Check q
            if q_clean is not None:
                q_matched = False
                for col_name, col_type in col_types.items():
                    val = record.get(col_name)
                    if val is None:
                        continue
                    if col_type == "str":
                        if q_clean in str(val).lower():
                            q_matched = True
                            break
                    elif col_type in ("int", "int_or_empty"):
                        if str(val) == q_clean:
                            q_matched = True
                            break
                if not q_matched:
                    continue

            filtered.append(record)

        total = len(filtered)

        # Sorting
        if sort_by is not None:
            reverse = order.lower() == "desc"

            def sort_key(rec: Mapping[str, Any]) -> Any:
                val = rec.get(sort_by)
                if val is None:
                    # Place None at end when asc, at start when desc
                    return (1, 0) if not reverse else (0, 0)
                return (0, val) if not reverse else (1, val)

            filtered.sort(key=sort_key, reverse=reverse)

        # Paginate
        page_records = filtered[offset : offset + limit]
        # Return copied dicts to ensure caller cannot modify catalog
        return [dict(r) for r in page_records], total

    def query_quarantine(
        self,
        entry_index: int | None = None,
        record_key: Any | None = None,
        offset: int = 0,
        limit: int = 50,
    ) -> tuple[list[dict[str, Any]], int]:
        """Query quarantined records."""
        filtered = []
        for q in self._quarantine:
            if entry_index is not None and q.entry_index != entry_index:
                continue
            if record_key is not None and str(q.record_key) != str(record_key):
                continue
            filtered.append(
                {
                    "entry_index": q.entry_index,
                    "table": q.table,
                    "record_key": q.record_key,
                    "reasons": list(q.reasons),
                    "native_verified": q.native_verified,
                    "value_under_applied_profile": _to_plain_data(q.value_under_applied_profile),
                }
            )
        total = len(filtered)
        return filtered[offset : offset + limit], total

    def query_overwrites(
        self,
        key: int | None = None,
        offset: int = 0,
        limit: int = 50,
    ) -> tuple[list[dict[str, Any]], int]:
        """Query skill overwrite records."""
        filtered = []
        for o in self._overwrites:
            if key is not None and o.key != key:
                continue
            filtered.append(
                {
                    "order": o.order,
                    "code_offset": o.code_offset,
                    "entry_index": o.entry_index,
                    "table": o.table,
                    "key": o.key,
                    "old_value": _to_plain_data(o.old_value),
                    "new_value": _to_plain_data(o.new_value),
                }
            )
        total = len(filtered)
        return filtered[offset : offset + limit], total

    def get_batch_info(self) -> dict[str, Any]:
        """Return batch metadata and validation summary."""
        return {
            "batch": self._manifest.get("batch", "batch_001"),
            "native_loader_confirmed": False,
            "manifest_files_count": len(self._manifest.get("files", {})),
            "csv_format": dict(self._manifest.get("csv_format", {})),
            "tables_summary": dict(self._validation.get("tables", {})),
            "validation_summary": dict(self._validation),
        }

    def get_missing_aptitudes(self) -> list[dict[str, Any]]:
        """Return pet aptitude missing records directly."""
        ds = self.get_dataset("pet_aptitude_missing")
        return [dict(r) for r in ds.records]

    def get_ambiguous_skills(self) -> list[dict[str, Any]]:
        """Return pet skill matches that are marked ambiguous."""
        ds = self.get_dataset("pet_skill_name_matches")
        return [dict(r) for r in ds.records if r.get("ambiguous") is True]
