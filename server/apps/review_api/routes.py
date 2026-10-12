"""Route handlers for Review Query API."""

from typing import Any
from fastapi import APIRouter, HTTPException, Query, Request, status
from fastapi.responses import JSONResponse

from mxsj_catalog.catalog import ReviewCatalog
from mxsj_catalog.errors import DatasetNotFoundError, RecordNotFoundError

from .schemas import (
    BatchInfoResponse,
    DatasetListResponse,
    DatasetMetaResponse,
    HealthResponse,
    OverwritesResponse,
    QuarantineResponse,
    RecordsResponse,
)

router = APIRouter()


def get_catalog(request: Request) -> ReviewCatalog:
    catalog = getattr(request.app.state, "catalog", None)
    if catalog is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={
                "code": "CATALOG_NOT_READY",
                "message": "Review catalog has not been loaded or initialization failed.",
                "details": {},
            },
        )
    return catalog


def _assert_no_unexpected_params(request: Request, allowed: set[str], endpoint_name: str) -> None:
    """Verify that no unexpected or misspelled query parameters were passed."""
    for param in request.query_params.keys():
        if param not in allowed:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "code": "INVALID_PARAMETER",
                    "message": f"Unknown query parameter '{param}' for {endpoint_name}. Allowed: {sorted(allowed)}",
                    "details": {"param": param},
                },
            )


@router.get("/health", response_model=HealthResponse)
def get_health(request: Request) -> HealthResponse:
    _assert_no_unexpected_params(request, set(), "health")
    catalog = get_catalog(request)
    datasets = catalog.list_datasets()
    total_records = sum(d["rows"] for d in datasets)
    return HealthResponse(
        status="ready",
        batch=catalog.get_batch_info().get("batch", "batch_001"),
        loaded_files_count=catalog.loaded_files_count,
        datasets_count=len(datasets),
        total_records_count=total_records,
    )


@router.get("/batch", response_model=BatchInfoResponse)
def get_batch(request: Request) -> BatchInfoResponse:
    _assert_no_unexpected_params(request, set(), "batch")
    catalog = get_catalog(request)
    info = catalog.get_batch_info()
    return BatchInfoResponse(**info)


@router.get("/datasets", response_model=DatasetListResponse)
def list_datasets(request: Request) -> DatasetListResponse:
    _assert_no_unexpected_params(request, set(), "datasets")
    catalog = get_catalog(request)
    items = catalog.list_datasets()
    return DatasetListResponse(
        total=len(items),
        datasets=[DatasetMetaResponse(**d) for d in items],
    )


@router.get("/datasets/{dataset_id}", response_model=DatasetMetaResponse)
def get_dataset_meta(dataset_id: str, request: Request) -> DatasetMetaResponse:
    _assert_no_unexpected_params(request, set(), f"datasets/{dataset_id}")
    catalog = get_catalog(request)
    try:
        ds = catalog.get_dataset(dataset_id)
    except DatasetNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "code": "DATASET_NOT_FOUND",
                "message": str(e),
                "details": {"dataset_id": dataset_id},
            },
        )
    source_entry = ds.schema.source_entry
    if isinstance(source_entry, tuple):
        source_entry = list(source_entry)
    return DatasetMetaResponse(
        id=ds.schema.id,
        filename=ds.schema.filename,
        rows=ds.schema.rows,
        primary_key=list(ds.schema.primary_key),
        notes=ds.schema.notes,
        source_entry=source_entry,
        source_table=ds.schema.source_table,
        columns=[{"name": c.name, "type": c.type} for c in ds.schema.columns],
    )


@router.get("/datasets/{dataset_id}/records", response_model=RecordsResponse)
def query_records(
    dataset_id: str,
    request: Request,
    offset: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=500),
    q: str | None = Query(None),
    sort_by: str | None = Query(None),
    order: str = Query("asc"),
) -> RecordsResponse:
    catalog = get_catalog(request)
    try:
        ds = catalog.get_dataset(dataset_id)
    except DatasetNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "code": "DATASET_NOT_FOUND",
                "message": str(e),
                "details": {"dataset_id": dataset_id},
            },
        )

    order_norm = order.strip().lower()
    if order_norm not in ("asc", "desc"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "code": "INVALID_PARAMETER",
                "message": f"Order parameter must be 'asc' or 'desc', got {order!r}",
                "details": {"param": "order", "value": order},
            },
        )

    col_types = {c.name: c.type for c in ds.schema.columns}
    col_types["_pk"] = "str"

    # Extract exact field filters from query params
    known_param_names = {"offset", "limit", "q", "sort_by", "order"}
    filters: dict[str, Any] = {}
    for param_name, param_val in request.query_params.items():
        if param_name not in known_param_names:
            if param_name not in col_types:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail={
                        "code": "INVALID_PARAMETER",
                        "message": f"Unknown filter column '{param_name}'. Available columns: {sorted(col_types.keys())}",
                        "details": {"param": param_name},
                    },
                )
            filters[param_name] = param_val

    try:
        records, total = catalog.query_records(
            dataset_id=dataset_id,
            offset=offset,
            limit=limit,
            q=q,
            filters=filters,
            sort_by=sort_by,
            order=order_norm,
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "code": "INVALID_PARAMETER",
                "message": str(e),
                "details": {},
            },
        )

    return RecordsResponse(
        dataset=ds.schema.id,
        total=total,
        offset=offset,
        limit=limit,
        count=len(records),
        records=records,
    )


@router.get("/datasets/{dataset_id}/records/{record_id:path}")
def get_single_record(
    dataset_id: str,
    record_id: str,
    request: Request,
) -> dict[str, Any]:
    _assert_no_unexpected_params(request, set(), "single record lookup")
    catalog = get_catalog(request)
    try:
        record = catalog.get_record(dataset_id, record_id)
    except DatasetNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "code": "DATASET_NOT_FOUND",
                "message": str(e),
                "details": {"dataset_id": dataset_id},
            },
        )

    if record is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "code": "RECORD_NOT_FOUND",
                "message": f"Record with id '{record_id}' not found in dataset '{dataset_id}'.",
                "details": {"dataset_id": dataset_id, "record_id": record_id},
            },
        )
    return record


@router.get("/quarantine", response_model=QuarantineResponse)
def get_quarantine(
    request: Request,
    entry_index: int | None = Query(None),
    record_key: str | None = Query(None),
    offset: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=500),
) -> QuarantineResponse:
    allowed_params = {"entry_index", "record_key", "offset", "limit"}
    _assert_no_unexpected_params(request, allowed_params, "quarantine")

    catalog = get_catalog(request)
    records, total = catalog.query_quarantine(
        entry_index=entry_index,
        record_key=record_key,
        offset=offset,
        limit=limit,
    )
    return QuarantineResponse(total=total, records=records)


@router.get("/overwrites", response_model=OverwritesResponse)
def get_overwrites(
    request: Request,
    key: int | None = Query(None),
    offset: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=500),
) -> OverwritesResponse:
    allowed_params = {"key", "offset", "limit"}
    _assert_no_unexpected_params(request, allowed_params, "overwrites")

    catalog = get_catalog(request)
    records, total = catalog.query_overwrites(
        key=key,
        offset=offset,
        limit=limit,
    )
    return OverwritesResponse(total=total, records=records)


@router.get("/missing-aptitudes")
def get_missing_aptitudes(request: Request) -> list[dict[str, Any]]:
    _assert_no_unexpected_params(request, set(), "missing-aptitudes")
    catalog = get_catalog(request)
    return catalog.get_missing_aptitudes()


@router.get("/ambiguous-skills")
def get_ambiguous_skills(request: Request) -> list[dict[str, Any]]:
    _assert_no_unexpected_params(request, set(), "ambiguous-skills")
    catalog = get_catalog(request)
    return catalog.get_ambiguous_skills()
