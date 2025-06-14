class ContextManagerException(Exception):
    pass

class ContextSyntaxError(ContextManagerException):
    pass



class ContextFileSyntaxError(ContextSyntaxError):
    pass

class ContextNecessaryFieldsMissingError(ContextFileSyntaxError):
    pass

class ContextFieldTypeError(ContextFileSyntaxError):
    pass

class ContextInvalidRoleError(ContextFileSyntaxError):
    pass



class ContextInvalidRoleError(ContextManagerException):
    pass