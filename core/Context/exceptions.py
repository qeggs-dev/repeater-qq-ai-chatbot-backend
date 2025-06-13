class ContextManagerException(Exception):
    pass


class ContextFileSyntaxError(ContextManagerException):
    pass

class ContextNecessaryFieldsMissingError(ContextFileSyntaxError):
    pass

class ContextFieldTypeError(ContextFileSyntaxError):
    pass

class ContextInvalidRoleError(ContextFileSyntaxError):
    pass