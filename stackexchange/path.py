from copy import copy
from functools import total_ordering

import six


@total_ordering
class StackExchangeAPIPathLevel(object):
    def __init__(self, name, position, writable=False):
        self.__name = name
        self.__position = position
        self.__writable = writable

    @property
    def name(self):
        return self.__name

    @property
    def position(self):
        return self.__position

    @property
    def writable(self):
        return self.__writable

    def to_tuple(self):
        return self.position, self.name, self.writable

    def __eq__(self, other):
        return self.position == other.position

    def __gt__(self, other):
        return self.position >= other.position

    def __hash__(self):
        return hash(self.position)

    def __repr__(self):
        return str(self.to_tuple())
    __str__ = __repr__


class StackExchangeAPIPath(object):
    def __init__(self, levels=None):
        """
        :param list[StackExchangeAPIPathLevel] levels:
        :return:
        """
        self._levels = set(levels or [])

    def _get_level_sequence(self):
        sorted_levels = sorted(self.levels)
        sequence = [level.position for level in sorted_levels]

        if sequence != list(six.moves.range(1, len(sequence) + 1)):
            raise ValueError(
                'API URL Path sequence has gaps: {}'.format(sequence)
            )

        return [
            level.name
            for level in sorted_levels
        ]

    def compile(self):
        return '/'.join(self._get_level_sequence())

    @property
    def levels(self):
        """
        :rtype: set[StackExchangeAPIPathLevel]
        """
        return frozenset(self._levels)

    @property
    def sorted_levels(self):
        """
        :rtype: list[StackExchangeAPIPathLevel]
        """
        return sorted(self._levels)

    @property
    def writable(self):
        """
        :rtype: bool
        """
        return any(level.writable for level in self.levels)

    @property
    def last(self):
        return self.sorted_levels[-1]

    def endswith(self, name):
        return self.last.name == name

    def __copy__(self):
        return self.__class__(self.levels)

    def __add__(self, other):
        return self.__class__(
            other.segments.union(self.levels)
        )

    def __iadd__(self, other):
        self._levels.union(other.levels)
        return self

    def add(self, name, offset=None, writable=False):
        """
        Add a new path level.
        :param name:
        :param offset:
        :param writable:
        :return:
        """
        levels = name.split('/')
        if offset is None:
            offset = 0
            if self._levels:
                offset = max(self.levels).position
            offset += 1

        for name in levels:
            self._levels.add(
                StackExchangeAPIPathLevel(
                    name=name,
                    position=offset,
                    writable=writable
                )
            )
        return self

    def __repr__(self):
        return '/{}'.format(self.compile())
    __str__ = __repr__


class StackExchangeAPIEndpoint(object):
    def __init__(self, path=None):
        """
        :param StackExchangeAPIPath|None path: the URL path for this endpoint.
        :return:
        """
        self._path = path or StackExchangeAPIPath()
        if path is None:
            self._path = self._path.add(
                offset=1,
                name=self.__class__.__name__.lower()
            )

    def request(self):
        """
        :rtype: StackExchangeAPIRequest
        """
        from stackexchange.http import StackExchangeAPIRequest
        return StackExchangeAPIRequest(self)

    def __copy__(self):
        return self.__class__(copy(self._path))

    def extend_with(self, name, offset=None, writable=False):
        """
        :rtype: StackExchangeAPIEndpoint
        """
        new_instance = copy(self)
        new_instance._path = new_instance.path.add(
            name=name,
            offset=offset,
            writable=writable
        )
        return new_instance

    @property
    def http_method(self):
        """
        :rtype: str
        """
        if self._path.writable:
            return 'POST'
        else:
            return 'GET'

    @property
    def path(self):
        """
        :rtype: StackExchangeAPIPath
        """
        return self._path

    @path.setter
    def path(self, value):
        """
        :param StackExchangeAPIPath value:
        :return:
        """
        value.compile()
        self._path = value

    def __str__(self):
        return '<{}@{}: [{} {}]>'.format(
            self.__class__.__name__,
            hex(id(self)),
            self.http_method,
            self._path
        )

    __repr__ = __str__
