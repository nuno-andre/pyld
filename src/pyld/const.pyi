from typing import AbstractSet


__copyright__: str
__license__: str
__version__: str


def get_intenv(var: str, default: int) -> int: ...


MAX_CONTEXT_URLS: int
MAX_ACTIVE_CONTEXTS: int
RESOLVED_CONTEXT_CACHE_MAX_SIZE: int
INVERSE_CONTEXT_CACHE_MAX_SIZE: int
XSD_BOOLEAN: str
XSD_DOUBLE: str
XSD_INTEGER: str
XSD_STRING: str
RDF: str
RDF_LIST: str
RDF_FIRST: str
RDF_REST: str
RDF_NIL: str
RDF_TYPE: str
RDF_LANGSTRING: str
RDF_JSON_LITERAL: str
JSON_LD_NS: str
LINK_HEADER_REL: str


def get_jsonld_version() -> str: ...


JSONLD_VERSION: str
KEYWORDS: AbstractSet[str]
