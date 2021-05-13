from collections.abc import Mapping
from functools import reduce


class frozendict(Mapping):
    '''Immutable mapping.
    '''
    __slots__ = '_dict', '_hash'

    def __init__(self, *args, **kwargs):
        self._dict = dict(*args, **kwargs)
        self._hash = None

    def __getitem__(self, key):
        return self._dict[key]

    def __contains__(self, key):
        return key in self._dict

    def copy(self, **items):
        return self.__class__(self, **items)

    def __iter__(self):
        return iter(self._dict)

    def __len__(self):
        return len(self._dict)

    def __repr__(self):
        return f'<{self.__class__.__name__} {self._dict}>'

    def __hash__(self):
        if self._hash is None:
            self._hash = reduce(
                lambda x, y: x ^ hash(y), self._dict.items(), 0)
        return self._hash
