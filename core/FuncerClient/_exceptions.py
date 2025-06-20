class FuncerClientException(Exception):
    """Base exception for FuncerClient"""
    pass


class UnderstandFormatError(FuncerClientException):
    """Raised when the response from the Funcer server is not in the expected format"""
    pass

class FormattingError(UnderstandFormatError):
    """Raised when the formatting of the request is incorrect"""
    pass

class FunctionNotFoundError(FuncerClientException):
    """Raised when the function is not found"""
    pass

class BadResponse(FuncerClientException):
    """Raised when the response from the Funcer server is not valid"""
    def __init__(self, message, code, body):
        self.code = code
        self.body = body
        self.message = message
        super().__init__(message)

    def __str__(self):
        return f"Bad response: {self.message} (code: {self.code})"
    
    def __repr__(self):
        return f"BadResponse(message={self.message}, code={self.code}, body={self.body})"