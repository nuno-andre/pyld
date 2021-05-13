"""
Remote document loader.

.. module:: jsonld.document_loader
  :synopsis: Remote document loader

.. moduleauthor:: Dave Longley
.. moduleauthor:: Mike Johnson
.. moduleauthor:: Tim McNamara <tim.mcnamara@okfn.org>
.. moduleauthor:: Olaf Conradi <olaf@conradi.org>
.. moduleauthor:: Nuno André <mail@nunoand.re>
"""
from typing import Any, Optional, Callable, Union
from urllib.parse import urlparse
import string
import re

from httpx import AsyncClient, Response, get as httpx_get

from .exceptions import JsonLdError, InvalidUrl, LoadDocumentError
from .jsonld import prepend_base
from .const import LINK_HEADER_REL
from .parse import parse_link_header


Loader = Callable[[str, dict[str, Any]], dict[str, Any]]

__all__ = ['sync_document_loader', 'async_document_loader']


VALID_CHARS = set(string.ascii_letters + string.digits + '-.:')
BASE_HEADERS = {'Accept': 'application/ld+json, application/json'}


def validate_url(url: str, secure: bool = False) -> None:
    pieces = urlparse(url)

    if (
        not all([pieces.scheme, pieces.netloc])
        or pieces.scheme not in ['http', 'https']
        or set(pieces.netloc) > VALID_CHARS
    ):
        raise InvalidUrl(
            'URL could not be dereferenced; only "http" and "https" '
            'URLs are supported.',
            {'url': url},
            code='loading document failed')

    if secure and pieces.scheme != 'https':
        raise InvalidUrl(
            'URL could not be dereferenced; secure mode enabled and '
            'the URL\'s scheme is not "https".',
            {'url': url},
            code='loading document failed')


def parse_response(response: Response, url: str) -> dict[str, Any]:
    content_type = response.headers.get('content-type') or 'application/octet-stream'

    doc = dict(contentType=content_type,
               contextUrl=None,
               documentUrl=str(response.url),
               document=response.json())

    link_header = response.headers.get('link')
    if link_header:
        linked_context = parse_link_header(link_header).get(
            LINK_HEADER_REL)
        # only 1 related link header permitted
        if linked_context and content_type != 'application/ld+json':
            if isinstance(linked_context, list):
                raise LoadDocumentError(
                    'URL could not be dereferenced, it has more '
                    'than one associated HTTP Link Header.',
                    {'url': url},
                    code='multiple context link headers')
            doc['contextUrl'] = linked_context['target']

        linked_alternate = parse_link_header(link_header).get('alternate')
        # if not JSON-LD, alternate may point there
        if (
            linked_alternate
            and linked_alternate.get('type') == 'application/ld+json'
            and not re.match(r'^application\/([\w\.\-]*?\+)?json$', content_type)
        ):
            doc.update(contentType='application/ld+json',
                       documentUrl=prepend_base(url, linked_alternate['target']))
    return doc


def sync_document_loader(secure: bool = False, **kwargs) -> Loader:
    """
    Create a synchronous document loader.

    Can be used to setup extra args such as verify, cert, timeout,
    or others.

    :param secure: require all requests to use HTTPS (default: False).
    :param **kwargs: extra keyword args for synchronous get() call.

    :return: the RemoteDocument loader function.
    """
    def loader(url: str, options=None):
        """
        Retrieves JSON-LD at the given URL.

        :param url: the URL to retrieve.

        :return: the RemoteDocument.
        """
        try:
            validate_url(url, secure=secure)
            options = options or {}
            headers = options.get('headers', BASE_HEADERS)
            response = httpx_get(url, headers=headers, **kwargs)

            return parse_response(response, url)

        except JsonLdError:
            raise
        except Exception as e:
            raise LoadDocumentError(
                'Could not retrieve a JSON-LD document from the URL.',
                code='loading document failed',
                cause=e)

    return loader


def async_document_loader(loop=None, secure: bool = False, **kwargs) -> Loader:
    """
    Create an asynchronous document loader.

    :param loop: the event loop used for processing HTTP requests.
    :param secure: require all requests to use HTTPS (default: False).
    :param **kwargs: extra keyword args for the async request get() call.

    :return: the RemoteDocument loader function.
    """
    import asyncio

    if loop is None:
        loop = asyncio.get_event_loop()

    async def async_loader(
            url: str, headers: dict[str, str]) -> dict[str, Any]:
        """
        Retrieves JSON-LD at the given URL asynchronously.

        :param url: the URL to retrieve.

        :return: the RemoteDocument.
        """
        try:
            validate_url(url, secure=secure)

            async with AsyncClient() as session:
                response = await session.get(url, headers=headers, **kwargs)

                return parse_response(response, url)

        except JsonLdError:
            raise
        except Exception as e:
            raise LoadDocumentError(
                'Could not retrieve a JSON-LD document from the URL.',
                code='loading document failed',
                cause=e)

    def loader(url: str, options: Optional[dict[str, str]] = None):
        """
        Retrieves JSON-LD at the given URL.

        :param url: the URL to retrieve.

        :return: the RemoteDocument.
        """
        return loop.run_until_complete(
            async_loader(url, (options or {}).get('headers', BASE_HEADERS))
        )

    return loader
