class ValidationError(Exception):
    """Raised when validation fails."""
    pass


class NotFoundError(Exception):
    """Raised when a resource is not found."""
    pass


class StorageError(Exception):
    """Raised when storage operations fail."""
    pass