class APIInfoException(Exception):
    """Base class for exceptions in this module."""
    pass


class APIGroupNotFoundError(APIInfoException):
    """Raised when an API group is not found."""
    pass

