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


class CompactError(JsonLdException):
    type = 'jsonld.CompactError'


class ContextUrlError(JsonLdException):
    type = 'jsonld.ContextUrlError'


class CyclicalContext(JsonLdException):
    type = 'jsonld.CyclicalContext'


class FlattenError(JsonLdException):
    type = 'jsonld.FlattenError'


class FrameError(JsonLdException):
    type = 'jsonld.FrameError'


class InvalidJsonLiteral(ValueError, JsonLdException):
    type = 'jsonld.InvalidJsonLiteral'


class InvalidUrl(JsonLdException):
    type = 'jsonld.InvalidUrl'


class LoadDocumentError(JsonLdException):
    type = 'jsonld.LoadDocumentError'


class NormalizeError(JsonLdException):
    type = 'jsonld.NormalizeError'


class NullRemoteDocument(JsonLdException):
    type = 'jsonld.NullRemoteDocument'

    def __init__(self, details=None, code=None, cause=None):
        msg = 'No remote document found at the given URL.'
        super().__init__(msg, details=details, code=code, cause=cause)


class ParseError(JsonLdException):
    type = 'jsonld.ParseError'


class ProcessingModeConflict(JsonLdException):
    type = 'jsonld.ProcessingModeConflict'


class RdfError(JsonLdException):
    type = 'jsonld.RdfError'


class UnknownFormat(JsonLdException):
    type = 'jsonld.UnknownFormat'

    def __init__(self, message, details=None, code=None, cause=None, format=None):
        if format:
            details = (details or {}).update({'format': format})
        super().__init__(message, details=details, code=code, cause=cause)


class UnsupportedVersion(JsonLdException):
    type = 'jsonld.UnsupportedVersion'
