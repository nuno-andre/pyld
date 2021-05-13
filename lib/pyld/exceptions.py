import traceback
import sys


class JsonLdError(Exception):
    """
    Base class for JSON-LD errors.
    """
    def __init__(self, message, type_, details=None, code=None, cause=None):
        super().__init__(self, message)
        self.type = type_
        self.details = details
        self.code = code
        self.cause = cause
        self.causeTrace = traceback.extract_tb(*sys.exc_info()[2:])

    def __str__(self):
        rval = str(self.args)
        rval += f'\nType: {self.type}'
        if self.code:
            rval += f'\nCode: {self.code}'
        if self.details:
            rval += f'\nDetails: {self.details}'
        if self.cause:
            rval += f'\nCause: {self.cause}'
            rval += ''.join(traceback.format_list(self.causeTrace))
        return rval


# TODO: transition class
class JsonLdException(JsonLdError):

    def __init__(self, message, details=None, code=None, cause=None):
        super().__init__(message, self.type, details, code, cause)


class JsonLdSyntaxError(JsonLdException):
    type = 'jsonld.SyntaxError'

    def __init__(self, message=None, details=None, code=None, cause=None):
        message = ': '.join(filter(None, ('Invalid JSON-LD syntax', message)))
        super().__init__(message, details, code, cause)


class LoadDocumentError(JsonLdException):
    type = 'jsonld.LoadDocumentError'


class ContextUrlError(JsonLdException):
    type = 'jsonld.ContextUrlError'


class InvalidUrl(JsonLdException):
    type = 'jsonld.InvalidUrl'
