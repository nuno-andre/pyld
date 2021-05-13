"""
Remote document loader using aiohttp.

.. module:: jsonld.documentloader.aiohttp
  :synopsis: Remote document loader using aiohttp

.. moduleauthor:: Olaf Conradi <olaf@conradi.org>
"""

import string
from urllib.parse import urlparse

from ..exceptions import JsonLdError, InvalidUrl, LoadDocumentError
from ..jsonld import parse_link_header, LINK_HEADER_REL, prepend_base


def aiohttp_document_loader(loop=None, secure=False, **kwargs):
    """
    Create an Asynchronous document loader using aiohttp.

    :param loop: the event loop used for processing HTTP requests.
    :param secure: require all requests to use HTTPS (default: False).
    :param **kwargs: extra keyword args for the aiohttp request get() call.

    :return: the RemoteDocument loader function.
    """
    import asyncio
    import aiohttp

    if loop is None:
        loop = asyncio.get_event_loop()

    async def async_loader(url, headers):
        """
        Retrieves JSON-LD at the given URL asynchronously.

        :param url: the URL to retrieve.

        :return: the RemoteDocument.
        """
        try:
            # validate URL
            pieces = urlparse(url)
            if (not all([pieces.scheme, pieces.netloc]) or
                pieces.scheme not in ['http', 'https'] or
                set(pieces.netloc) > set(
                    string.ascii_letters + string.digits + '-.:')):
                raise InvalidUrl(
                    'URL could not be dereferenced; '
                    'only "http" and "https" URLs are supported.',
                    {'url': url},
                    code='loading document failed')
            if secure and pieces.scheme != 'https':
                raise InvalidUrl(
                    'URL could not be dereferenced; '
                    'secure mode enabled and '
                    'the URL\'s scheme is not "https".',
                    {'url': url},
                    code='loading document failed')
            async with aiohttp.ClientSession(loop=loop) as session:
                async with session.get(url,
                                       headers=headers,
                                       **kwargs) as response:
                    # Allow any content_type in trying to parse json
                    # similar to requests library
                    json_body = await response.json(content_type=None)
                    content_type = response.headers.get('content-type')
                    if not content_type:
                        content_type = 'application/octet-stream'
                    doc = {
                        'contentType': content_type,
                        'contextUrl': None,
                        'documentUrl': response.url.human_repr(),
                        'document': json_body
                    }
                    link_header = response.headers.get('link')
                    if link_header:
                        linked_context = parse_link_header(link_header).get(
                            LINK_HEADER_REL)
                        # only 1 related link header permitted
                        if linked_context and content_type != 'application/ld+json':
                            if isinstance(linked_context, list):
                                raise LoadDocumentError(
                                    'URL could not be dereferenced, '
                                    'it has more than one '
                                    'associated HTTP Link Header.',
                                    {'url': url},
                                    code='multiple context link headers')
                            doc['contextUrl'] = linked_context['target']
                        linked_alternate = parse_link_header(link_header).get('alternate')
                        # if not JSON-LD, alternate may point there
                        if (linked_alternate and
                                linked_alternate.get('type') == 'application/ld+json' and
                                not re.match(r'^application\/(\w*\+)?json$', content_type)):
                            doc['contentType'] = 'application/ld+json'
                            doc['documentUrl'] = prepend_base(url, linked_alternate['target'])

                    return doc
        except JsonLdError:
            raise
        except Exception as cause:
            raise LoadDocumentError(
                'Could not retrieve a JSON-LD document from the URL.',
                code='loading document failed',
                cause=cause)

    def loader(url, options={}):
        """
        Retrieves JSON-LD at the given URL.

        :param url: the URL to retrieve.

        :return: the RemoteDocument.
        """
        return loop.run_until_complete(async_loader(
            url,
            options.get('headers', {'Accept': 'application/ld+json, application/json'})))

    return loader
