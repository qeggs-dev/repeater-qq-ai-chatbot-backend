class ContextManagerException(Exception):
    pass

class ContextSyntaxError(ContextManagerException):
    pass



class ContextLoadingSyntaxError(ContextSyntaxError):
    pass

class ContextNecessaryFieldsMissingError(ContextLoadingSyntaxError):
    pass

class ContextFieldTypeError(ContextSyntaxError):
    pass

class ContextInvalidRoleError(ContextSyntaxError):
    pass