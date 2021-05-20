from .types import Object, ParsedUrl
from typing import Any, Union, Optional, Dict, List, Tuple, Callable, Match, Pattern


REGEX_BCP47: Pattern
KEYWORD: Pattern
ABSOLUTE_IRI: Pattern

_url: Callable[[str], Optional[Match]]


def parse_url(url: str) -> ParsedUrl: ...


def unparse_url(parsed: Union[Dict, List, Tuple, ParsedUrl]) -> str: ...


_link_header: Callable[[str], Optional[Match]]
_link_header_entries: Callable[[str], List[str]]
_link_header_params: Callable[[str], List[str]]


def parse_link_header(header: str) -> Object[Any]: ...


ESCAPED: Dict[int, str]


def parse_nquads(input_: str) -> Object[Any]: ...


def to_nquad(triple: Any, graph_name: Optional[str]) -> str: ...


def to_nquads(dataset: Object[Any]) -> str: ...
