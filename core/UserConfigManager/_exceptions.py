class ConfigManagerException(Exception):
    """Base class for exceptions in this module."""
    pass

class UnintelligibleConfigFormat(ConfigManagerException):
    """Raised when the config file is not in a supported format."""
    pass

class KeyNotFoundError(ConfigManagerException):
    """Raised when a key is not found."""
    pass

class EnvError(ConfigManagerException):
    """Base class for exceptions in this module."""
    pass


class EnvNotFoundError(EnvError):
    """Exception raised when environment variable is not found."""
    pass

class UnintelligibleBatchFormat(EnvError):
    """Exception raised when batch format is not intelligible."""
    pass

class EnvTypeError(EnvError):
    """Exception raised when environment variable type is not supported."""
    pass