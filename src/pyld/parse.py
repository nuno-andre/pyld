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

    return ''.join((
        f'{parsed.scheme}:' if parsed.scheme else '',
        f'//{parsed.authority}' if parsed.authority is not None else '',
        parsed.path,
        f'?{parsed.query}' if parsed.query is not None else '',
        f'#{parsed.fragment}' if parsed.fragment is not None else '',
    ))
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

ESCAPED = str.maketrans(
    {'\\':  r'\\', '\t':  r'\t', '\n':  r'\n', '\r':  r'\r', '"': r'\"'})


def _compare_rdf_triples(t1, t2) -> bool:
    """
    Compares two RDF triples for equality.

    :param t1: the first triple.
    :param t2: the second triple.

    :return: True if the triples are the same, False if not.
    """
    for attr in ['subject', 'predicate', 'object']:
        if (t1[attr]['type'] != t2[attr]['type'] or
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
            s1, s2, p, o1, o2, o3, o4, o5, n1, n2 = _quad(line).groups()
        except AttributeError:
            raise ParseError('Error while parsing N-Quads invalid quad.', line=i)

        # get subject
        if s1 is not None:
            subject = {'type': 'IRI', 'value': s1}
        else:
            subject = {'type': 'blank node', 'value': s2}

        # get object
        if o1 is not None:
            object_ = {'type': 'IRI', 'value': o1}
        elif o2 is not None:
            object_ = {'type': 'blank node', 'value': o2}
        else:
            object_ = {'type': 'literal'}
            unescaped = (o3
                         .replace(r'\"', '"')
                         .replace(r'\t', '\t')
                         .replace(r'\n', '\n')
                         .replace(r'\r', '\r')
                         .replace(r'\\', '\\'))
            if o4 is not None:
                object_['datatype'] = o4
            elif o5 is not None:
                object_['datatype'] = RDF_LANGSTRING
                object_['language'] = o5
            else:
                object_['datatype'] = XSD_STRING
            object_['value'] = unescaped

        # create RDF triple
        triple = {
            'subject': subject,
            'object': object_,
            'predicate': {'type': 'IRI', 'value': p},
        }

        # get graph name ('@default' is used for the default graph)
        name = n1 if n1 is not None else n2 if n2 is not None else '@default'

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


def to_nquad(triple, graph_name=None):
    """
    Converts an RDF triple and graph name to an N-Quad string (a single
    quad).

    :param triple: the RDF triple or quad to convert (a triple or quad
        may be passed, if a triple is passed then `graph_name` should be
        given to specify the name of the graph the triple is in, `None`
        for the default graph).
    :param graph_name: the name of the graph containing the triple, None
        for the default graph.

    :return: the N-Quad string.
    """
    s = triple['subject']
    p = triple['predicate']
    o = triple['object']
    g = triple.get('name', {'value': graph_name})['value']

    # is subject an IRI?
    quad = f'<{s["value"]}> ' if s['type'] == 'IRI' else f'{s["value"]} '

    # is property an IRI?
    quad += f'<{p["value"]}> ' if p['type'] == 'IRI' else f'{p["value"]} '

    # object is IRI, bnode, or literal
    if o['type'] == 'IRI':
        quad += f'<{o["value"]}>'
    elif(o['type'] == 'blank node'):
        quad += o['value']
    else:
        escaped = o['value'].translate(ESCAPED)
        quad += f'"{escaped}"'
        if o['datatype'] == RDF_LANGSTRING:
            if o['language']:
                quad += f'@{o["language"]}'
        elif o['datatype'] != XSD_STRING:
            quad += f'^^<{o["datatype"]}>'

    # graph
    if g is not None:
        quad += f' <{g}>' if g[0:2] != '_:' else f' {g}'

    return quad + ' .\n'


def to_nquads(dataset):
    """
    Converts an RDF dataset to N-Quads.

    :param dataset: the RDF dataset to convert.

    :return: the N-Quads string.
    """
    quads = []
    for graph_name, triples in dataset.items():
        for triple in triples:
            if graph_name == '@default':
                graph_name = None
            quads.append(to_nquad(triple, graph_name))
    quads.sort()
    return ''.join(quads)
# endregion
