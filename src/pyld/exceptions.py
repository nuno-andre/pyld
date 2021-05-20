import traceback
import sys


class JsonLdError(Exception):
    """
    Base class for JSON-LD errors.
    """
    def __init__(self, message: str, code=None, cause=None, **kwargs):
        super().__init__(self, message)
        self.details = kwargs
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


class JsonLdSyntaxError(JsonLdError):
    type = 'jsonld.SyntaxError'

    def __init__(self, message=None, **kwargs):
        message = ': '.join(filter(None, ('Invalid JSON-LD syntax', message)))
        super().__init__(message, **kwargs)


class CompactError(JsonLdError):
    type = 'jsonld.CompactError'


class ContextUrlError(JsonLdError):
    type = 'jsonld.ContextUrlError'


class CyclicalContext(JsonLdError):
    type = 'jsonld.CyclicalContext'


class FlattenError(JsonLdError):
    type = 'jsonld.FlattenError'


class FrameError(JsonLdError):
    type = 'jsonld.FrameError'


class InvalidJsonLiteral(JsonLdError, ValueError):
    type = 'jsonld.InvalidJsonLiteral'


class InvalidUrl(JsonLdError):
    type = 'jsonld.InvalidUrl'


class LoadDocumentError(JsonLdError):
    type = 'jsonld.LoadDocumentError'


class NormalizeError(JsonLdError):
    type = 'jsonld.NormalizeError'


class NullRemoteDocument(JsonLdError):
    type = 'jsonld.NullRemoteDocument'

    def __init__(self, **kwargs):
        message = 'No remote document found at the given URL.'
        super().__init__(message, **kwargs)


class ParseError(JsonLdError):
    type = 'jsonld.ParseError'


class ProcessingModeConflict(JsonLdError):
    type = 'jsonld.ProcessingModeConflict'


class RdfError(JsonLdError):
    type = 'jsonld.RdfError'


class UnknownFormat(JsonLdError):
    type = 'jsonld.UnknownFormat'


class UnsupportedVersion(JsonLdError):
    type = 'jsonld.UnsupportedVersion'
