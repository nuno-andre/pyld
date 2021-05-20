from typing import Any, Callable
from httpx import Response

Loader = Callable[[str, dict[str, Any]], dict[str, Any]]
def validate_url(url: str, secure: bool) -> None: ...
def parse_response(response: Response, url: str) -> dict[str, Any]: ...
def sync_document_loader(secure: bool, **kwargs: Any) -> Loader: ...
def async_document_loader(loop: Any, secure: bool, **kwargs: Any) -> Loader: ...
