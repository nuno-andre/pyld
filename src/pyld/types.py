from typing import NamedTuple, Optional
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


class IdentifierIssuer(object):
    """
    An IdentifierIssuer issues unique identifiers, keeping track of any
    previously issued identifiers.

    :param prefix: the prefix to use ('<prefix><counter>').
    """

    def __init__(self, prefix):
        self.prefix = prefix
        self.counter = 0
        self.existing = dict()

    def get_id(self, old=None):
        """
        Gets the new identifier for the given old identifier, where if no old
        identifier is given a new identifier will be generated.

        :param [old]: the old identifier to get the new identifier for.

        :return: the new identifier.
        """
        # return existing old identifier
        if old and old in self.existing:
            return self.existing[old]

        # get next identifier
        id_ = self.prefix + str(self.counter)
        self.counter += 1

        # save mapping
        if old is not None:
            self.existing[old] = id_

        return id_

    def __contains__(self, old):
        return old in self.existing

    def has_id(self, old):
        """
        Returns True if the given old identifier has already been assigned a
        new identifier.

        :param old: the old identifier to check.

        :return: True if the old identifier has been assigned a new identifier,
          False if not.
        """
        return old in self.existing


class ParsedUrl(NamedTuple):
    scheme: str
    authority: Optional[str]
    path: str
    query: Optional[str]
    fragment: Optional[str]


# class IdentifierIssuer(dict):
#     """
#     An IdentifierIssuer issues unique identifiers, keeping track of any
#     previously issued identifiers.

#     :param prefix: the prefix to use ('<prefix><counter>').
#     """
#     __slots__ = 'prefix', '__counter', 'order'

#     def __init__(self, prefix: str) -> None:
#         self.prefix = prefix
#         self.__counter = 0
#         self.order = []

#     def __setitem__(self, key: Optional[str], value: str) -> None:
#         if key is not None:
#             super().__setitem__(key, value)
#             self.order.append(key)

#     def __missing__(self, old: Optional[str]) -> str:
#         # get next identifier
#         id_ = self[old] = f'{self.prefix}{len(self)}'
#         self.__counter += 1
#         return id_

#     def __len__(self) -> int:
#         # note this represents the number of issued indentifiers,
#         #   not cached (stored) identifiers.
#         return self.__counter

#     def get(self, old: Optional[str] = None):
#         # if no old identifier is given a new identifier will be
#         #   generated.
#         return self[old]

#     get_id = get
#     has_id = lambda s, x: x in s
