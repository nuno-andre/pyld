from .types import IdentifierIssuer, Object, Options
from typing import Any, Dict, Iterator, List, TypeVar
from hashlib._hashlib import HASH

T = TypeVar('T')
Quad = Dict[str, Dict[str, Any]]


def permutations(elements: List[T]) -> Iterator[List[T]]: ...


class URDNA2015:
    blank_node_info: Dict
    hash_to_blank_nodes: Dict
    canonical_issuer: IdentifierIssuer
    quads: List[Object[Any]]
    POSITIONS: Dict[str, str]

    def __init__(self) -> None: ...
    def main(self, dataset: Object, options: Options): ...
    def hash_first_degree_quads(self, id_: Any): ...
    def modify_first_degree_component(self, id_: str, component: Object[Any], key: Any): ...
    def hash_related_blank_node(self, related: Any, quad: Any, issuer: Any, position: Any): ...
    def get_related_predicate(self, quad: Quad): ...
    def hash_n_degree_quads(self, id_: Any, issuer: IdentifierIssuer) -> Any: ...
    def create_hash_to_related(self, id_: Any, issuer: Any): ...
    def create_hash(self) -> HASH: ...
    def hash_nquads(self, nquads: List[Any]) -> str: ...


class URGNA2012(URDNA2015):
    def modify_first_degree_component(self, id_: Any, component: Any, key: Any): ...
    def get_related_predicate(self, quad: Quad): ...
    def create_hash_to_related(self, id_: Any, issuer: Any): ...
    def create_hash(self) -> HASH: ...
