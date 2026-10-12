"""Review catalog management and query interface."""

import copy
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
    ALL_REQUIRED_FILES,
    FILE_TO_SHORT_ID,
    REQUIRED_CSV_FILES,
    REQUIRED_EVIDENCE_FILES,
    SHORT_NAME_MAP,
    _freeze_dict,
    load_raw_dataset,
    normalize_dataset_id,
    verify_file_integrity,
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
        loaded_files_count: int,
    ) -> None:
        self._base_dir = base_dir
        self._manifest = manifest
        self._validation = validation
        self._provenance = provenance
        self._datasets = datasets
        self._quarantine = quarantine
        self._overwrites = overwrites
        self._loaded_files_count = loaded_files_count

    @property
    def loaded_files_count(self) -> int:
        return self._loaded_files_count

    @classmethod
    def load(cls, base_dir: str | Path | None = None) -> "ReviewCatalog":
        """Load and strictly validate all catalog files according to manifest."""
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

        try:
            with open(manifest_path, "r", encoding="utf-8") as f:
                manifest_data = json.load(f)
        except json.JSONDecodeError as e:
            raise CatalogIntegrityError(f"Corrupted manifest JSON: {manifest_path}") from e

        files_meta = manifest_data.get("files")
        if not isinstance(files_meta, dict):
            raise CatalogIntegrityError("Manifest missing 'files' dictionary")

        # 1. Enforce that all required batch_001 files are declared in manifest
        missing_declarations = ALL_REQUIRED_FILES - set(files_meta.keys())
        if missing_declarations:
            raise CatalogIntegrityError(
                f"Manifest missing required files declaration: {sorted(missing_declarations)}"
            )

        # Check for path traversal or unexpected files in manifest
        resolved_base = base_dir.resolve()
        for rel_path in files_meta.keys():
            target_path = (base_dir / rel_path).resolve()
            try:
                target_path.relative_to(resolved_base)
            except ValueError:
                raise CatalogIntegrityError(
                    f"Path traversal detected: '{rel_path}' is outside batch directory"
                )
            if rel_path not in ALL_REQUIRED_FILES:
                raise CatalogIntegrityError(
                    f"Unexpected file declared in manifest: '{rel_path}'"
                )

        # 2. Verify integrity of all non-CSV evidence files declared in manifest
        for ev_path in REQUIRED_EVIDENCE_FILES:
            ev_meta = files_meta[ev_path]
            verify_file_integrity(ev_path, ev_meta, base_dir)

        # 3. Load CSV datasets
        datasets: dict[str, Dataset] = {}
        for rel_path in sorted(REQUIRED_CSV_FILES):
            meta = files_meta[rel_path]
            dataset = load_raw_dataset(rel_path, meta, base_dir)
            short_id = dataset.schema.id
            datasets[short_id] = dataset
            # Also index by relative file path for convenience
            datasets[rel_path] = dataset

        # 4. Load quarantine.jsonl
        quarantine_list: list[QuarantineRecord] = []
        quarantine_path = base_dir / "quarantine.jsonl"
        with open(quarantine_path, "r", encoding="utf-8") as f:
            for line_no, line in enumerate(f, start=1):
                line = line.strip()
                if not line:
                    continue
                try:
                    item = json.loads(line)
                except json.JSONDecodeError as e:
                    raise CatalogIntegrityError(
                        f"Corrupted JSON in quarantine.jsonl line {line_no}"
                    ) from e
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

        # 5. Load overwrite_evidence.jsonl
        overwrites_list: list[OverwriteEvidence] = []
        overwrites_path = base_dir / "overwrite_evidence.jsonl"
        with open(overwrites_path, "r", encoding="utf-8") as f:
            for line_no, line in enumerate(f, start=1):
                line = line.strip()
                if not line:
                    continue
                try:
                    item = json.loads(line)
                except json.JSONDecodeError as e:
                    raise CatalogIntegrityError(
                        f"Corrupted JSON in overwrite_evidence.jsonl line {line_no}"
                    ) from e
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

        # 6. Load validation.json
        validation_path = base_dir / "validation.json"
        try:
            with open(validation_path, "r", encoding="utf-8") as f:
                validation_data = json.load(f)
        except json.JSONDecodeError as e:
            raise CatalogIntegrityError(f"Corrupted JSON in validation.json: {e}") from e

        # 7. Load maps_npcs/provenance.json
        provenance_path = base_dir / "maps_npcs" / "provenance.json"
        try:
            with open(provenance_path, "r", encoding="utf-8") as f:
                provenance_data = json.load(f)
        except json.JSONDecodeError as e:
            raise CatalogIntegrityError(f"Corrupted JSON in provenance.json: {e}") from e

        # Total loaded files = verified files in manifest + manifest.json itself
        total_loaded_files = len(files_meta) + 1

        return cls(
            base_dir=base_dir,
            manifest=_freeze_dict(manifest_data),
            validation=_freeze_dict(validation_data),
            provenance=_freeze_dict(provenance_data),
            datasets=datasets,
            quarantine=tuple(quarantine_list),
            overwrites=tuple(overwrites_list),
            loaded_files_count=total_loaded_files,
        )

    def list_datasets(self) -> list[dict[str, Any]]:
        """List metadata for all distinct datasets (returns deep copies)."""
        res: list[dict[str, Any]] = []
        for short_id, rel_path in SHORT_NAME_MAP.items():
            if short_id in self._datasets:
                ds = self._datasets[short_id]
                source_entry = ds.schema.source_entry
                if isinstance(source_entry, tuple):
                    source_entry = list(source_entry)
                res.append(
                    {
                        "id": ds.schema.id,
                        "filename": ds.schema.filename,
                        "rows": ds.schema.rows,
                        "primary_key": list(ds.schema.primary_key),
                        "notes": ds.schema.notes,
                        "source_entry": source_entry,
                        "source_table": ds.schema.source_table,
                        "columns": [
                            {"name": c.name, "type": c.type} for c in ds.schema.columns
                        ],
                    }
                )
        return copy.deepcopy(res)

    def get_dataset(self, dataset_id: str) -> Dataset:
        """Fetch dataset by ID or raise DatasetNotFoundError."""
        normalized = normalize_dataset_id(dataset_id)
        if normalized in self._datasets:
            return self._datasets[normalized]
        if dataset_id in self._datasets:
            return self._datasets[dataset_id]
        raise DatasetNotFoundError(f"Dataset '{dataset_id}' does not exist.")

    def get_record(self, dataset_id: str, pk: str) -> dict[str, Any] | None:
        """Fetch single record by primary key (returns deep copy)."""
        dataset = self.get_dataset(dataset_id)
        row = dataset.get_by_pk(pk)
        if row is None:
            return None
        return copy.deepcopy(dict(row))

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

        order_norm = order.strip().lower()
        if order_norm not in ("asc", "desc"):
            raise ValueError(f"Order parameter must be 'asc' or 'desc', got {order!r}")

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
            match = True
            for k, expected_v in normalized_filters.items():
                if record.get(k) != expected_v:
                    match = False
                    break
            if not match:
                continue

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
            reverse = order_norm == "desc"

            def sort_key(rec: Mapping[str, Any]) -> Any:
                val = rec.get(sort_by)
                if val is None:
                    return (1, 0) if not reverse else (0, 0)
                return (0, val) if not reverse else (1, val)

            filtered.sort(key=sort_key, reverse=reverse)

        # Paginate and return deep copies
        page_records = filtered[offset : offset + limit]
        return [copy.deepcopy(dict(r)) for r in page_records], total

    def query_quarantine(
        self,
        entry_index: int | None = None,
        record_key: Any | None = None,
        offset: int = 0,
        limit: int = 50,
    ) -> tuple[list[dict[str, Any]], int]:
        """Query quarantined records (returns deep copies)."""
        if offset < 0:
            raise ValueError(f"Offset must be >= 0, got {offset}")
        if limit < 1 or limit > 500:
            raise ValueError(f"Limit must be between 1 and 500, got {limit}")

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
        return copy.deepcopy(filtered[offset : offset + limit]), total

    def query_overwrites(
        self,
        key: int | None = None,
        offset: int = 0,
        limit: int = 50,
    ) -> tuple[list[dict[str, Any]], int]:
        """Query skill overwrite records (returns deep copies)."""
        if offset < 0:
            raise ValueError(f"Offset must be >= 0, got {offset}")
        if limit < 1 or limit > 500:
            raise ValueError(f"Limit must be between 1 and 500, got {limit}")

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
        return copy.deepcopy(filtered[offset : offset + limit]), total

    def get_batch_info(self) -> dict[str, Any]:
        """Return batch metadata and validation summary (deep copy)."""
        manifest_dict = _to_plain_data(self._manifest)
        validation_dict = _to_plain_data(self._validation)
        info = {
            "batch": manifest_dict.get("batch", "batch_001"),
            "native_loader_confirmed": False,
            "manifest_files_count": len(manifest_dict.get("files", {})),
            "csv_format": manifest_dict.get("csv_format", {}),
            "tables_summary": validation_dict.get("tables", {}),
            "validation_summary": validation_dict,
        }
        return copy.deepcopy(info)

    def get_validation_summary(self) -> dict[str, Any]:
        """Return validation summary (deep copy)."""
        return copy.deepcopy(_to_plain_data(self._validation))

    def get_missing_aptitudes(self) -> list[dict[str, Any]]:
        """Return pet aptitude missing records directly (deep copy)."""
        ds = self.get_dataset("pet_aptitude_missing")
        return copy.deepcopy([dict(r) for r in ds.records])

    def get_ambiguous_skills(self) -> list[dict[str, Any]]:
        """Return pet skill matches that are marked ambiguous (deep copy)."""
        ds = self.get_dataset("pet_skill_name_matches")
        return copy.deepcopy([dict(r) for r in ds.records if r.get("ambiguous") is True])
