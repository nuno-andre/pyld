from collections.abc import Mapping
from typing import (
    Any, Dict, Iterator, List, Literal, NamedTuple, Optional,
    TypedDict, TypeVar, Union,
)

NoneType = type(None)
Json: Any
KT = TypeVar('KT')
VT = TypeVar('VT')
Object = Dict[str, VT]


class frozendict(Mapping[KT, VT]):
    _dict: Dict[KT, VT]
    _hash: Optional[int]
    def __init__(self, *args: Any, **kwargs: Any) -> None: ...
    def __getitem__(self, key: KT) -> VT: ...
    def __contains__(self, key: object) -> bool: ...
    def copy(self, **items: Any) -> 'frozendict': ...
    def __iter__(self) -> Iterator: ...
    def __len__(self) -> int: ...
    def __hash__(self) -> int: ...


class IdentifierIssuer:
    prefix: str
    counter: int
    existing: Dict[str, Any]
    def __init__(self, prefix: str) -> None: ...
    def get_id(self, old: Optional[str]) -> str: ...
    def __contains__(self, old: str) -> bool: ...
    def has_id(self, old: Any) -> bool: ...


class ParsedUrl(NamedTuple):
    scheme: str
    authority: Optional[str]
    path: str
    query: Optional[str]
    fragment: Optional[str]


class AnyOptions(TypedDict, total=False):
    algorithm: Literal['URDNA2015', 'URGNA2012']
    base: str
    bnodesToClear: List[str]
    compactArrays: bool
    contextResolver: Any  # TODO: ContextResolver
    documentLoader: Any  # TODO: Loader
    embed: str  # TODO: keyword?
    expandContext: Any
    extractAllScripts: bool
    format: Literal['application/n-quads', 'application/nquads']
    framing: bool
    graph: bool
    headers: Object[str]
    inputFormat: Literal['application/n-quads', 'application/nquads']
    isFrame: bool
    is11: bool
    keepFreeFloatingNodes: bool
    link: Object[List[str]]
    omitGraph: bool
    produceGeneralizedRdf: bool
    rdfDirection: Optional[Literal['i18n-datatype']]
    useNativeTypes: bool
    useRdfType: bool
    skipExpansion: bool


class Options10(AnyOptions, total=False):
    processingMode: Literal['json-ld-1.0']


class Options11(AnyOptions, total=False):
    processingMode: Literal['json-ld-1.1']


Options = Union[Options10, Options11]


Context10 = TypedDict(
    'Context10',
    {
        'mappings': Object[Object[Any]],
        'previousContext': Object[Any],
        '_uuid': str,
        'processingMode': Literal['json-ld-1.0'],
        '@base': str,
        '@language': str,
        '@protected': bool,
        '@version': float,  # TODO: 1.0
        '@vocab': str,
    },
    total=False,
)


Context11 = TypedDict(
    'Context11',
    {
        'mappings': Object[Object[Any]],
        'previousContext': Object[Any],
        '_uuid': str,
        'processingMode': Literal['json-ld-1.1'],
        '@base': str,
        '@language': str,
        '@protected': bool,
        '@version': float,  # TODO: 1.1
        '@vocab': str,
        '@import': str,
    },
    total=False,
)


Context = Union[Context10, Context11]
