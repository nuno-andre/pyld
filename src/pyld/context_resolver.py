"""
Context Resolver for managing remote contexts.

.. module:: context_resolver
  :synopsis: Creates a ContextResolver

.. moduleauthor:: Dave Longley
.. moduleauthor:: Gregg Kellogg <gregg@greggkellogg.net>
"""
from cachetools import LRUCache
from c14n.Canonicalize import canonicalize
from .types import Mapping
from .exceptions import JsonLdSyntaxError, ContextUrlError, InvalidUrl
from .const import MAX_CONTEXT_URLS, MAX_ACTIVE_CONTEXTS


class ResolvedContext:
    """
    A cached contex document, with a cache indexed by referencing active
    context.
    """
    def __init__(self, document):
        """
        Creates a ResolvedContext with caching for processed contexts
        relative to some other Active Context.
        """
        # processor-specific RDF parsers
        self.document = document
        self.cache = LRUCache(maxsize=MAX_ACTIVE_CONTEXTS)

    def get_processed(self, active_ctx):
        """
        Returns any processed context for this resolved context relative
        to an active context.
        """
        return self.cache.get(active_ctx['_uuid'])

    def set_processed(self, active_ctx, processed_ctx):
        """
        Sets any processed context for this resolved context relative to
        an active context.
        """
        self.cache[active_ctx['_uuid']] = processed_ctx


class ContextResolver:
    """
    Resolves and caches remote contexts.
    """
    def __init__(self, shared_cache, document_loader):
        """
        Creates a ContextResolver.
        """
        # processor-specific RDF parsers
        self.per_op_cache = {}
        self.shared_cache = shared_cache
        self.document_loader = document_loader

    def resolve(self, active_ctx, context, base, cycles=None):
        """
        Resolve a context.

        :param active_ctx: the current active context.
        :param context: the context to resolve.
        :param base: the absolute URL to use for making url absolute.
        :param cycles: the maximum number of times to recusively fetch
            contexts (default MAX_CONTEXT_URLS).
        """
        if cycles is None:
            cycles = set()

        # process `@context`
        if isinstance(context, Mapping) and '@context' in context:
            context = context['@context']

        # context is one or more contexts
        if not isinstance(context, list):
            context = [context]

        # resolve each context in the array
        all_resolved = []
        for ctx in context:
            if isinstance(ctx, str):
                resolved = self._get(ctx)
                if not resolved:
                    resolved = self._resolve_remote_context(
                        active_ctx, ctx, base, cycles)

                # add to output and continue
                if isinstance(resolved, list):
                    all_resolved.extend(resolved)
                else:
                    all_resolved.append(resolved)
            elif not ctx:
                all_resolved.append(ResolvedContext(False))
            elif not isinstance(ctx, Mapping):
                raise JsonLdSyntaxError('@context must be an object.',
                                        context=ctx, code='invalid local context')
            else:
                # context is an object, get/create `ResolvedContext` for it
                key = canonicalize(dict(ctx)).decode('UTF-8')
                resolved = self._get(key)
                if not resolved:
                    # create a new static `ResolvedContext` and cache it
                    resolved = ResolvedContext(ctx)
                    self._cache_resolved_context(key, resolved, 'static')
                all_resolved.append(resolved)

        return all_resolved

    def _get(self, key):
        resolved = self.per_op_cache.get(key)
        if not resolved:
            tag_map = self.shared_cache.get(key)
            if tag_map:
                resolved = tag_map.get('static')
                if resolved:
                    self.per_op_cache[key] = resolved
        return resolved

    def _cache_resolved_context(self, key, resolved, tag):
        self.per_op_cache[key] = resolved
        if tag:
            tag_map = self.shared_cache.get(key)
            if not tag_map:
                tag_map = {}
                self.shared_cache[key] = tag_map
            tag_map[tag] = resolved
        return resolved

    def _resolve_remote_context(self, active_ctx, url, base, cycles):
        from .jsonld import prepend_base

        # resolve relative URL and fetch context
        url = prepend_base(base, url)
        context, remote_doc = self._fetch_context(active_ctx, url, cycles)

        # update base according to remote document and resolve any relative URLs
        base = remote_doc.get('documentUrl', url)
        self._resolve_context_urls(context, base)

        # resolve, cache, and return context
        resolved = self.resolve(active_ctx, context, base, cycles)
        self._cache_resolved_context(url, resolved, remote_doc.get('tag'))
        return resolved

    def _fetch_context(self, active_ctx, url, cycles):
        from .jsonld import load_document

        # check for max context URLs fetched during a resolve operation
        if len(cycles) > MAX_CONTEXT_URLS:
            if active_ctx.get('processingMode') == 'json-ld-1.0':
                code = 'recursive context inclusion'
            else:
                code = 'context overflow'
            raise ContextUrlError('Maximum number of @context URLs exceeded.',
                                  max=MAX_CONTEXT_URLS, code=code)

        # check for context URL cycle
        # shortcut to avoid extra work that would eventually hit the max above
        if url in cycles:
            if active_ctx.get('processingMode') == 'json-ld-1.0':
                code = 'recursive context inclusion'
            else:
                code = 'context overflow'
            raise ContextUrlError('Cyclical @context URLs detected.',
                                  url=url, code=code)

        # track cycles
        cycles.add(url)

        try:
            remote_doc = load_document(
                url,
                {'documentLoader': self.document_loader},
                requestProfile='http://www.w3.org/ns/json-ld#context',
            )
            context = remote_doc.get('document', url)
        except Exception as e:
            raise InvalidUrl(
                'Dereferencing a URL did not result in a valid JSON-LD object. '
                'Possible causes are an inaccessible URL perhaps due to '
                'a same-origin policy (ensure the server uses CORS if you are '
                'using client-side JavaScript), too many redirects, a '
                'non-JSON response, or more than one HTTP Link Header was '
                'provided for a remote context.',
                url=url, cause=e, code='loading remote context failed')

        # ensure ctx is an object
        if not isinstance(context, Mapping):
            raise InvalidUrl(
                'Dereferencing a URL did not result in a JSON object. The '
                'response was valid JSON, but it was not a JSON object.',
                url=url, code='invalid remote context')

        # use empty context if no @context key is present
        if '@context' not in context:
            context = {'@context': {}}

        # append @context URL to context if given
        if remote_doc['contextUrl']:
            if not isinstance(context['@context'], list):
                context['@context'] = [context['@context']]
            context['@context'].append(remote_doc['contextUrl'])

        return (context, remote_doc)

    def _resolve_context_urls(self, context, base):
        """
        Resolve all relative `@context` URLs in the given context by inline
        replacing them with absolute URLs.

        :param context: the context.
        :param base: the base IRI to use to resolve relative IRIs.
        """
        from .jsonld import prepend_base

        if not isinstance(context, Mapping):
            return

        ctx = context.get('@context')

        if isinstance(ctx, str):
            context['@context'] = prepend_base(base, ctx)
            return

        if isinstance(ctx, list):
            for num, element in enumerate(ctx):
                if isinstance(element, str):
                    ctx[num] = prepend_base(base, element)
                elif isinstance(element, Mapping):
                    self. _resolve_context_urls({'@context': element}, base)
            return

        if not isinstance(ctx, Mapping):
            # no @context URLs can be found in non-object
            return

        # ctx is an object, resolve any context URLs in terms
        # (Iterate using keys() as items() returns a copy we can't modify)
        for _, definition in ctx.items():
            self._resolve_context_urls(definition, base)
