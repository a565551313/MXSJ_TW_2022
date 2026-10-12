"""Pydantic schemas for Review Query API responses."""

from typing import Any
from pydantic import BaseModel, Field


class ErrorDetail(BaseModel):
    code: str
    message: str
    details: dict[str, Any] = Field(default_factory=dict)


class ErrorResponse(BaseModel):
    error: ErrorDetail


class HealthResponse(BaseModel):
    status: str
    batch: str
    loaded_files_count: int
    datasets_count: int
    total_records_count: int


class ColumnSchema(BaseModel):
    name: str
    type: str


class DatasetMetaResponse(BaseModel):
    id: str
    filename: str
    rows: int
    primary_key: list[str]
    notes: str = ""
    source_entry: int | list[int] | None = None
    source_table: str | None = None
    columns: list[ColumnSchema]


class DatasetListResponse(BaseModel):
    total: int
    datasets: list[DatasetMetaResponse]


class RecordsResponse(BaseModel):
    dataset: str
    total: int
    offset: int
    limit: int
    count: int
    records: list[dict[str, Any]]


class QuarantineResponse(BaseModel):
    total: int
    records: list[dict[str, Any]]


class OverwritesResponse(BaseModel):
    total: int
    records: list[dict[str, Any]]


class BatchInfoResponse(BaseModel):
    batch: str
    native_loader_confirmed: bool = False
    manifest_files_count: int
    csv_format: dict[str, Any]
    tables_summary: dict[str, Any]
    validation_summary: dict[str, Any]
