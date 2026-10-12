"""Data models and immutable definitions for MXSJ review catalog."""

from dataclasses import dataclass, field
from types import MappingProxyType
from typing import Any, Mapping


@dataclass(frozen=True)
class ColumnDef:
    """Definition of a dataset column."""
    name: str
    type: str


@dataclass(frozen=True)
class DatasetSchema:
    """Schema metadata for a review dataset."""
    id: str
    filename: str
    rows: int
    primary_key: tuple[str, ...]
    columns: tuple[ColumnDef, ...]
    notes: str = ""
    source_entry: tuple[int, ...] | int | None = None
    source_table: str | None = None
    csv_format: str = ""
    schema_document: str = ""


@dataclass(frozen=True)
class Dataset:
    """An immutable dataset containing verified records."""
    schema: DatasetSchema
    records: tuple[Mapping[str, Any], ...]
    index_by_pk: Mapping[str, Mapping[str, Any]]

    def get_by_pk(self, pk: str) -> Mapping[str, Any] | None:
        return self.index_by_pk.get(pk)


@dataclass(frozen=True)
class QuarantineRecord:
    """Quarantined review record with raw byte evidence."""
    entry_index: int
    table: str
    record_key: Any
    reasons: tuple[str, ...]
    native_verified: bool
    value_under_applied_profile: Mapping[str, Any]


@dataclass(frozen=True)
class OverwriteEvidence:
    """Overwrite evidence for skill entries."""
    order: int
    code_offset: int
    entry_index: int
    table: str
    key: int
    old_value: Mapping[str, Any]
    new_value: Mapping[str, Any]
