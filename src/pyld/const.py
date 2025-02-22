from os import getenv


__copyright__ = 'Copyright (c) 2011-2018 Digital Bazaar, Inc.'
__license__ = 'New BSD license'
__version__ = '2.1.0-dev'


def get_intenv(var, default):
    try:
        return int(getenv(f'PYLD_{var}', default))
    except ValueError:
        return default


MAX_CONTEXT_URLS = get_intenv('MAX_CONTEXT_URLS', 10)
MAX_ACTIVE_CONTEXTS = get_intenv('MAX_ACTIVE_CONTEXTS', 10)
RESOLVED_CONTEXT_CACHE_MAX_SIZE = get_intenv('RESOLVED_CONTEXT_CACHE_MAX_SIZE', 100)
INVERSE_CONTEXT_CACHE_MAX_SIZE = get_intenv('INVERSE_CONTEXT_CACHE_MAX_SIZE', 20)

# XSD constants
XSD_BOOLEAN = 'http://www.w3.org/2001/XMLSchema#boolean'
XSD_DOUBLE = 'http://www.w3.org/2001/XMLSchema#double'
XSD_INTEGER = 'http://www.w3.org/2001/XMLSchema#integer'
XSD_STRING = 'http://www.w3.org/2001/XMLSchema#string'

# RDF constants
RDF = 'http://www.w3.org/1999/02/22-rdf-syntax-ns#'
RDF_LIST = f'{RDF}List'
RDF_FIRST = f'{RDF}first'
RDF_REST = f'{RDF}rest'
RDF_NIL = f'{RDF}nil'
RDF_TYPE = f'{RDF}type'
RDF_LANGSTRING = f'{RDF}langString'
RDF_JSON_LITERAL = f'{RDF}JSON'

# JSON-LD Namespace
JSON_LD_NS = 'http://www.w3.org/ns/json-ld#'
LINK_HEADER_REL = f'{JSON_LD_NS}context'


def get_jsonld_version():
    env = getenv('PYLD_JSONLD_VERSION')
    if env and env.endswith('1.0'):
        return 'json-ld-1.0'
    return 'json-ld-1.1'


JSONLD_VERSION = get_jsonld_version()
KEYWORDS = frozenset((
    # JSON-LD keywords
    '@base',
    '@container',
    '@context',
    '@default',
    '@direction',
    '@embed',
    '@explicit',
    '@first',
    '@graph',
    '@id',
    '@import',
    '@included',
    '@index',
    '@json',
    '@language',
    '@list',
    '@nest',
    '@none',
    '@omitDefault',
    '@propagate',
    '@protected',
    '@preserve',
    '@requireAll',
    '@reverse',
    '@set',
    '@type',
    '@value',
    '@version',
    '@vocab',
))
