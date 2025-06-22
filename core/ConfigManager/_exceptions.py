class ConfigManagerException(Exception):
    """Base class for exceptions in this module."""
    pass

class UnintelligibleBatchFormat(ConfigManagerException):
    """Raised when the batch format is not intelligible."""
    pass
