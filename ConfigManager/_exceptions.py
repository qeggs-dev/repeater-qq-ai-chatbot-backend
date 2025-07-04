class ConfigError(Exception):
    """Base class for exceptions in this module."""
    pass

class ConfigSyntaxError(ConfigError):
    """Exception raised for errors in the input.

    Attributes:
        message -- explanation of the error
        errors -- pydantic errors
    """

    def __init__(self, message: str, errors:list):
        self.message = message
        self.errors = errors
    
    def __str__(self):
        import json
        return f"{self.message} {json.dumps(self.errors, indent=4, ensure_ascii=False)}"