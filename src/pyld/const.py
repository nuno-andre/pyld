from os import getenv


__copyright__ = 'Copyright (c) 2011-2018 Digital Bazaar, Inc.'
__license__ = 'New BSD license'
__version__ = '2.1.0-dev'


MAX_CONTEXT_URLS = getenv('PYLD_MAX_CONTEXT_URLS', 10)
MAX_ACTIVE_CONTEXTS = getenv('PYLD_MAX_ACTIVE_CONTEXTS', 10)
RESOLVED_CONTEXT_CACHE_MAX_SIZE = getenv('PYLD_RESOLVED_CONTEXT_CACHE_MAX_SIZE', 100)
INVERSE_CONTEXT_CACHE_MAX_SIZE = getenv('PYLD_INVERSE_CONTEXT_CACHE_MAX_SIZE', 20)


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
