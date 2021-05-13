"""
Remote document loader using Requests.

.. module:: jsonld.documentloader.requests
  :synopsis: Remote document loader using Requests

.. moduleauthor:: Dave Longley
.. moduleauthor:: Mike Johnson
.. moduleauthor:: Tim McNamara <tim.mcnamara@okfn.org>
.. moduleauthor:: Olaf Conradi <olaf@conradi.org>
"""
import string
from urllib.parse import urlparse

from ..exceptions import JsonLdError, InvalidUrl, LoadDocumentError
from ..jsonld import parse_link_header, LINK_HEADER_REL, prepend_base


def requests_document_loader(secure=False, **kwargs):
    """
    Create a Requests document loader.

    Can be used to setup extra Requests args such as verify, cert, timeout,
    or others.

    :param secure: require all requests to use HTTPS (default: False).
    :param **kwargs: extra keyword args for Requests get() call.

    :return: the RemoteDocument loader function.
    """
    import requests

    def loader(url, options={}):
        """
        Retrieves JSON-LD at the given URL.

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
            headers = options.get('headers')
            if headers is None:
                headers = {
                    'Accept': 'application/ld+json, application/json'
                }
            response = requests.get(url, headers=headers, **kwargs)

            content_type = response.headers.get('content-type')
            if not content_type:
                content_type = 'application/octet-stream'
            doc = {
                'contentType': content_type,
                'contextUrl': None,
                'documentUrl': response.url,
                'document': response.json()
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

    return loader
