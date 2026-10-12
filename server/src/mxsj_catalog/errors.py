"""Errors for MXSJ review catalog loading layer."""

class CatalogError(Exception):
    """Base exception for all catalog errors."""
    pass


class CatalogIntegrityError(CatalogError):
    """Raised when file hash, byte size, or row count does not match manifest."""
    pass


class CatalogSchemaError(CatalogError):
    """Raised when CSV header columns do not match manifest columns."""
    pass


class CatalogValueError(CatalogError):
    """Raised when field value cannot be strictly converted to defined type."""
    pass


class CatalogKeyError(CatalogError):
    """Raised when duplicate primary key is encountered or key columns are missing."""
    pass


class DatasetNotFoundError(CatalogError):
    """Raised when requested dataset does not exist."""
    pass


class RecordNotFoundError(CatalogError):
    """Raised when requested record cannot be found in dataset."""
    pass
