class NotFoundError(Exception):
    """Exception raised when a resource is not found"""

    pass


class DuplicateError(Exception):
    """Exception raised when a resource already exists"""

    pass
