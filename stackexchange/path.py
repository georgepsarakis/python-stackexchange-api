from functools import total_ordering
from copy import copy
import operator
import six


@total_ordering
class StackExchangeAPIPathSegment(object):
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
        return self.name, self.position, self.writable

    def __eq__(self, other):
        return self.position == other.position

    def __gt__(self, other):
        return self.position >= other.position

    def __hash__(self):
        return hash(self.to_tuple())

    def __repr__(self):
        return str(self.to_tuple())


class StackExchangeAPIPath(object):
    def __init__(self, segments=None):
        if segments is None:
            self._segments = set()
        else:
            self._segments = set(segments)

    def _get_segment_sequence(self):
        sorted_segments = sorted(self.segments)

        sequence = list(
            map(
                operator.attrgetter('position'),
                sorted_segments
            )
        )

        if sequence != list(six.moves.range(1, len(sequence) + 1)):
            raise ValueError

        path = []
        for segment in sorted_segments:
            if len(path) < segment.position:
                path.append(segment.name)
            else:
                path[segment.position - 1] = segment.name
        return path

    def compile(self):
        path = self._get_segment_sequence()
        return '/'.join(path)

    @property
    def segments(self):
        return frozenset(self._segments)

    @property
    def last_segment(self):
        return self._get_segment_sequence()[-1]

    @property
    def writable(self):
        return any(map(operator.attrgetter('writable'), self.segments))

    def __copy__(self):
        return self.__class__(self.segments)

    def __add__(self, other):
        return self.__class__(
            other.segments.union(self.segments)
        )

    def __iadd__(self, other):
        self._segments.union(other.segments)
        return self

    def add_segment(self, position, name, writable=False):
        if position is None:
            if self._segments:
                sorted_segments = sorted(self._segments, reverse=True)
                max_position = sorted_segments[0].position
                position = max_position + 1
            else:
                position = 1

        new_segment = StackExchangeAPIPathSegment(name, position, writable)
        for segment in self.segments:
            if segment >= new_segment:
                self._segments.discard(segment)

        self._segments.add(new_segment)
        return self

    def __repr__(self):
        return '/{}'.format(self.compile())


class StackExchangeAPIURLPath(object):
    def __init__(self, path=None):
        self._path = path or StackExchangeAPIPath()
        if path is None:
            self._path = self._path.add_segment(
                1,
                self.__class__.__name__.lower()
            )

    def __copy__(self):
        return self.__class__(copy(self._path))

    def extend_path(self, *args, **kwargs):
        """
        :rtype: StackExchangeAPIURLPath
        """
        new_instance = copy(self)
        new_instance._path = new_instance.path.add_segment(*args, **kwargs)
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

    def __str__(self):
        return '<{}@{}: [{} {}]>'.format(
            self.__class__.__name__,
            hex(id(self)),
            self.http_method,
            self._path
        )

    __repr__ = __str__


class StackExchangeAPIEndpoint(StackExchangeAPIURLPath):
    def request(self):
        """
        :rtype: StackExchangeAPIRequest
        """
        from stackexchange.http import StackExchangeAPIRequest
        return StackExchangeAPIRequest(self)
