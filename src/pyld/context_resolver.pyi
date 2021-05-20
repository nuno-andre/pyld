from collections.abc import Mapping, MutableMapping, Set
from typing import Any, Optional, List, Dict, Callable, Tuple


class ResolvedContext:
    document: Any
    cache: MutableMapping[str, Any]
    def __init__(self, document: Any) -> None: ...
    def get_processed(self, active_ctx: Any): ...
    def set_processed(self, active_ctx: Any, processed_ctx: Any) -> None: ...


class ContextResolver:
    per_op_cache: Dict[str, Any]
    shared_cache: Mapping
    document_loader: Callable

    def __init__(
        self,
        shared_cache: Mapping,
        document_loader: Callable,
    ) -> None: ...

    def resolve(
        self,
        active_ctx: Any,
        context: Any,
        base: Any,
        cycles: Optional[Set[str]]
    ) -> List[Any]: ...

    def _get(self, key: Any) -> Any: ...

    def _cache_resolved_context(
        self,
        key: Any,
        resolved: Any,
        tag: Any,
    ) -> Any: ...

    def _resolve_remote_context(
        self,
        active_ctx: Any,
        url: Any,
        base: Any,
        cycles: Optional[Set[str]],
    ) -> List[Any]: ...

    def _fetch_context(
        self,
        active_ctx: Any,
        url: str,
        cycles: Set[str],
    ) -> Tuple[Dict[str, Any], Dict[str, Any]]: ...

    def _resolve_context_urls(
        self,
        context: Mapping[str, Any],
        base: Any
    ) -> None: ...
