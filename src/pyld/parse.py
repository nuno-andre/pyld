import re

from .exceptions import ParseError
from .types import ParsedUrl
from .const import XSD_STRING, RDF_LANGSTRING


__all__ = [
    'REGEX_BCP47', 'KEYWORD', 'ABSOLUTE_IRI',
    'parse_url', 'unparse_url', 'parse_link_header',
]


REGEX_BCP47 = re.compile(r'^[A-Z]{1,8}(-[A-Z0-9]{1,8})*$', re.I)
KEYWORD = re.compile(r'^@[A-Z]+$', re.I)
ABSOLUTE_IRI = re.compile(r'^([A-Z][A-Z0-9+-.]*|_):[^\s]*$', re.I)


# region URL
_url = re.compile(
    # regex from RFC 3986
    r'^(?:([^:/?#]+):)?(?://([^/?#]*))?([^?#]*)(?:\?([^#]*))?(?:#(.*))?').match


def parse_url(url):
    # remove default http and https ports
    g = list(_url(url).groups())
    if (
        (g[0] == 'https' and g[1].endswith(':443'))
        or (g[0] == 'http' and g[1].endswith(':80'))
    ):
        g[1] = g[1][:g[1].rfind(':')]
    return ParsedUrl(*g)


def unparse_url(parsed):
    if isinstance(parsed, dict):
        parsed = ParsedUrl(**parsed)
    elif isinstance(parsed, (list, tuple)):
        parsed = ParsedUrl(*parsed)

    rval = ''
    if parsed.scheme:
        rval += f'{parsed.scheme}:'
    if parsed.authority is not None:
        rval += f'//{parsed.authority}'
    rval += parsed.path
    if parsed.query is not None:
        rval += f'?{parsed.query}'
    if parsed.fragment is not None:
        rval += f'#{parsed.fragment}'
    return rval
# endregion


# region LINK HEADER
_link_header = re.compile(
    r'\s*<([^>]*?)>\s*(?:;\s*(.*))?').search
_link_header_entries = re.compile(
    r'(?:<[^>]*?>|"[^"]*?"|[^,])+').findall
_link_header_params = re.compile(
    r'(.*?)=(?:(?:"([^"]*?)")|([^"]*?))\s*(?:(?:;\s*)|$)').findall


def parse_link_header(header):
    """
    Parses a link header. The results will be key'd by the value of "rel".

    Link: <http://json-ld.org/contexts/person.jsonld>; \
      rel="http://www.w3.org/ns/json-ld#context"; type="application/ld+json"

    Parses as: {
      'http://www.w3.org/ns/json-ld#context': {
        target: http://json-ld.org/contexts/person.jsonld,
        type: 'application/ld+json'
      }
    }

    If there is more than one "rel" with the same IRI, then entries in the
    resulting map for that "rel" will be lists.

    :param header: the link header to parse.

    :return: the parsed result.
    """
    rval = {}

    # split on unbracketed/unquoted commas
    for entry in _link_header_entries(header):
        match = _link_header(entry)
        if not match:
            continue
        match = match.groups()
        result = {'target': match[0]}
        params = match[1]
        for match in _link_header_params(params):
            result[match[0]] = match[2] if match[1] is None else match[1]
        rel = result.get('rel', '')
        if isinstance(rval.get(rel), list):
            rval[rel].append(result)
        elif rel in rval:
            rval[rel] = [rval[rel], result]
        else:
            rval[rel] = result

    return rval
# endregion


# region N-QUADS
def _nquads_functions():
    # define partial regexes
    iri = '(?:<([^:]+:[^>]*)>)'
    bnode = '(_:(?:[A-Za-z][A-Za-z0-9]*))'
    plain = r'"([^"\\]*(?:\\.[^"\\]*)*)"'
    datatype = rf'(?:\^\^{iri})'
    language = '(?:@([a-zA-Z]+(?:-[a-zA-Z0-9]+)*))'
    literal = f'(?:{plain}(?:{datatype}|{language})?)'
    ws = r'[ \t]+'
    wso = r'[ \t]*'

    # define quad part regexes
    subject = f'(?:{iri}|{bnode}){ws}'
    prop = f'{iri}{ws}'
    obj = f'(?:{iri}|{bnode}|{literal}){wso}'
    graph = rf'(?:\.|(?:(?:{iri}|{bnode}){wso}\.))'

    # Note: Notice that the graph position does not include literals
    #   even though they are specified as a possible value in the
    #   N-Quads note (http://sw.deri.org/2008/07/n-quads/).
    # This is intentional, as literals in that position are not
    #   supported by the RDF data model or the JSON-LD data model.
    # See: https://github.com/digitalbazaar/pyld/pull/19

    # full quad regex
    quad = re.compile(rf'^{wso}{subject}{prop}{obj}{graph}{wso}$').search
    empty = re.compile(rf'^{wso}$').search
    eoln = re.compile(r'(?:\r\n)|(?:\n)|(?:\r)').split

    return quad, empty, eoln


_quad, _empty, _eoln = _nquads_functions()


def _compare_rdf_triples(t1, t2):
    """
    Compares two RDF triples for equality.

    :param t1: the first triple.
    :param t2: the second triple.

    :return: True if the triples are the same, False if not.
    """
    for attr in ['subject', 'predicate', 'object']:
        if(t1[attr]['type'] != t2[attr]['type'] or
                t1[attr]['value'] != t2[attr]['value']):
            return False

    if t1['object'].get('language') != t2['object'].get('language'):
        return False
    if t1['object'].get('datatype') != t2['object'].get('datatype'):
        return False

    return True


def parse_nquads(input_):
    """
    Parses RDF in the form of N-Quads.

    :param input_: the N-Quads input to parse.

    :return: an RDF dataset.
    """
    # build RDF dataset
    dataset = {}

    # split N-Quad input into lines and skip empty lines
    for i, line in enumerate(_eoln(input_), 1):
        if _empty(line):
            continue

        # parse quad
        try:
            match = _quad(line).groups()
        except AttributeError:
            raise ParseError('Error while parsing N-Quads invalid quad.', line=i)

        # get subject
        if match[0] is not None:
            subject = {'type': 'IRI', 'value': match[0]}
        else:
            subject = {'type': 'blank node', 'value': match[1]}

        # get object
        if match[3] is not None:
            object_ = {'type': 'IRI', 'value': match[3]}
        elif match[4] is not None:
            object_ = {'type': 'blank node', 'value': match[4]}
        else:
            object_ = {'type': 'literal'}
            unescaped = (
                match[5]
                .replace(r'\"', '"')
                .replace(r'\t', '\t')
                .replace(r'\n', '\n')
                .replace(r'\r', '\r')
                .replace(r'\\', '\\'))
            if match[6] is not None:
                object_['datatype'] = match[6]
            elif match[7] is not None:
                object_['datatype'] = RDF_LANGSTRING
                object_['language'] = match[7]
            else:
                object_['datatype'] = XSD_STRING
            object_['value'] = unescaped

        # create RDF triple
        triple = {
            'subject': subject,
            'object': object_,
            'predicate': {'type': 'IRI', 'value': match[2]},
        }

        # get graph name ('@default' is used for the default graph)
        if match[8] is not None:
            name = match[8]
        elif match[9] is not None:
            name = match[9]
        else:
            name = '@default'

        # initialize graph in dataset
        if name not in dataset:
            dataset[name] = [triple]
        # add triple if unique to its graph
        else:
            unique = True
            triples = dataset[name]
            for t in dataset[name]:
                if _compare_rdf_triples(t, triple):
                    unique = False
                    break
            if unique:
                triples.append(triple)

    return dataset
# endregion
