from os import getenv


__copyright__ = 'Copyright (c) 2011-2018 Digital Bazaar, Inc.'
__license__ = 'New BSD license'
__version__ = '2.1.0-dev'


MAX_CONTEXT_URLS = getenv('PYLD_MAX_CONTEXT_URLS', 10)
MAX_ACTIVE_CONTEXTS = getenv('PYLD_MAX_ACTIVE_CONTEXTS', 10)
RESOLVED_CONTEXT_CACHE_MAX_SIZE = getenv('PYLD_RESOLVED_CONTEXT_CACHE_MAX_SIZE', 100)
INVERSE_CONTEXT_CACHE_MAX_SIZE = getenv('PYLD_INVERSE_CONTEXT_CACHE_MAX_SIZE', 20)

# XSD constants
XSD_BOOLEAN = 'http://www.w3.org/2001/XMLSchema#boolean'
XSD_DOUBLE = 'http://www.w3.org/2001/XMLSchema#double'
XSD_INTEGER = 'http://www.w3.org/2001/XMLSchema#integer'
XSD_STRING = 'http://www.w3.org/2001/XMLSchema#string'

# RDF constants
RDF = 'http://www.w3.org/1999/02/22-rdf-syntax-ns#'
RDF_LIST = RDF + 'List'
RDF_FIRST = RDF + 'first'
RDF_REST = RDF + 'rest'
RDF_NIL = RDF + 'nil'
RDF_TYPE = RDF + 'type'
RDF_LANGSTRING = RDF + 'langString'
RDF_JSON_LITERAL = RDF + 'JSON'

# JSON-LD Namespace
JSON_LD_NS = 'http://www.w3.org/ns/json-ld#'
LINK_HEADER_REL = JSON_LD_NS + 'context'


def get_jsonld_version():
    env = getenv('PYLD_JSONLD_VERSION')
    if env and env.endswith('1.0'):
        return 'json-ld-1.0'
    return 'json-ld-1.1'


JSONLD_VERSION = get_jsonld_version()
KEYWORDS = set((
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
