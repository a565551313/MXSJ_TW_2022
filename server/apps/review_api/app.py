"""FastAPI application factory for Review Query API."""

from contextlib import asynccontextmanager
import sys
from pathlib import Path
from typing import Any, AsyncIterator

_SRC_DIR = Path(__file__).resolve().parent.parent.parent / "src"
if str(_SRC_DIR) not in sys.path:
    sys.path.insert(0, str(_SRC_DIR))

from fastapi import FastAPI, HTTPException, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from mxsj_catalog.catalog import ReviewCatalog
from mxsj_catalog.errors import CatalogError, DatasetNotFoundError, RecordNotFoundError

from .config import API_PREFIX, DEFAULT_BATCH_DIR
from .routes import router


def create_app(
    catalog: ReviewCatalog | None = None,
    batch_dir: str | Path | None = None,
) -> FastAPI:
    """Create and configure FastAPI application."""

    target_batch_dir = Path(batch_dir).resolve() if batch_dir else DEFAULT_BATCH_DIR
    loaded_catalog: ReviewCatalog | None = None

    if catalog is not None:
        loaded_catalog = catalog
    else:
        try:
            loaded_catalog = ReviewCatalog.load(target_batch_dir)
        except CatalogError:
            # Catalog failed to initialize due to corruptions or missing files
            loaded_catalog = None

    @asynccontextmanager
    async def lifespan(app: FastAPI) -> AsyncIterator[None]:
        app.state.catalog = loaded_catalog
        yield

    app = FastAPI(
        title="MXSJ Review Browser API",
        version="1.0.0",
        description="Read-only catalog loading layer and query API for batch_001 review data.",
        lifespan=lifespan,
    )
    app.state.catalog = loaded_catalog

    # Allow CORS for development and frontend browser access
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=False,
        allow_methods=["GET", "OPTIONS", "HEAD"],
        allow_headers=["*"],
    )

    @app.exception_handler(404)
    async def not_found_handler(request: Request, exc: Any) -> JSONResponse:
        if isinstance(exc, HTTPException):
            detail = exc.detail
            if isinstance(detail, dict) and "code" in detail:
                return JSONResponse(
                    status_code=exc.status_code,
                    content={"error": detail},
                )
            return JSONResponse(
                status_code=exc.status_code,
                content={
                    "error": {
                        "code": "NOT_FOUND",
                        "message": str(detail),
                        "details": {},
                    }
                },
            )
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={
                "error": {
                    "code": "NOT_FOUND",
                    "message": "The requested API endpoint was not found.",
                    "details": {"path": request.url.path},
                }
            },
        )

    @app.exception_handler(405)
    async def method_not_allowed_handler(request: Request, exc: Any) -> JSONResponse:
        if isinstance(exc, HTTPException):
            detail = exc.detail
            if isinstance(detail, dict) and "code" in detail:
                return JSONResponse(
                    status_code=exc.status_code,
                    content={"error": detail},
                )
        return JSONResponse(
            status_code=status.HTTP_405_METHOD_NOT_ALLOWED,
            content={
                "error": {
                    "code": "METHOD_NOT_ALLOWED",
                    "message": "Method not allowed. This is a read-only review API.",
                    "details": {},
                }
            },
        )

    @app.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
        detail = exc.detail
        if isinstance(detail, dict) and "code" in detail:
            return JSONResponse(
                status_code=exc.status_code,
                content={"error": detail},
            )
        code = "HTTP_ERROR"
        if exc.status_code == 404:
            code = "NOT_FOUND"
        elif exc.status_code == 400:
            code = "INVALID_PARAMETER"
        elif exc.status_code == 405:
            code = "METHOD_NOT_ALLOWED"
        elif exc.status_code == 503:
            code = "CATALOG_NOT_READY"
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": {
                    "code": code,
                    "message": str(detail),
                    "details": {},
                }
            },
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(
        request: Request, exc: RequestValidationError
    ) -> JSONResponse:
        errors = exc.errors()
        msg = "; ".join(f"{'.'.join(str(loc) for loc in e['loc'])}: {e['msg']}" for e in errors)
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "error": {
                    "code": "INVALID_PARAMETER",
                    "message": f"Validation failed: {msg}",
                    "details": {"validation_errors": errors},
                }
            },
        )

    @app.exception_handler(DatasetNotFoundError)
    async def dataset_not_found_handler(
        request: Request, exc: DatasetNotFoundError
    ) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={
                "error": {
                    "code": "DATASET_NOT_FOUND",
                    "message": str(exc),
                    "details": {},
                }
            },
        )

    @app.exception_handler(RecordNotFoundError)
    async def record_not_found_handler(
        request: Request, exc: RecordNotFoundError
    ) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={
                "error": {
                    "code": "RECORD_NOT_FOUND",
                    "message": str(exc),
                    "details": {},
                }
            },
        )

    @app.exception_handler(Exception)
    async def generic_exception_handler(request: Request, exc: Exception) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "error": {
                    "code": "INTERNAL_SERVER_ERROR",
                    "message": "An internal server error occurred.",
                    "details": {},
                }
            },
        )

    app.include_router(router, prefix=API_PREFIX)
    return app
