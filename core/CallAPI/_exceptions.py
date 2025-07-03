class CallApiException(Exception):
    """Base class for exceptions in this module."""
    pass


class ModelNotFoundError(CallApiException):
    """Exception raised when a model is not found.

    Attributes:
        model_name -- name of the model that was not found
    """

    def __init__(self, model_name: str):
        self.model_name = model_name
        self.message = f"Model '{model_name}' not found"
        super().__init__(self.message)
    
    def __str__(self):
        return self.message

class APIConnectionError(CallApiException):
    """Exception raised when the API connection fails."""
    pass
