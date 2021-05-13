""" The PyLD module is used to process JSON-LD. """
from . import jsonld
from .__about__ import __version__  # noqa: F401
from .context_resolver import ContextResolver

__all__ = ['jsonld', 'ContextResolver']
