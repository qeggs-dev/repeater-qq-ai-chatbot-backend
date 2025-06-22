class EnvManagerError(Exception):
    """Base class for exceptions in this module."""
    pass


class EnvNotFoundError(EnvManagerError):
    """Exception raised when environment variable is not found."""
    pass

class UnintelligibleBatchFormat(EnvManagerError):
    """Exception raised when batch format is not intelligible."""
    pass

class EnvTypeError(EnvManagerError):
    """Exception raised when environment variable type is not supported."""
    pass