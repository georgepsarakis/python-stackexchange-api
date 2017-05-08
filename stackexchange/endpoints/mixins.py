import six

from stackexchange.path import StackExchangeAPIEndpoint


class StackExchangeAPIPartialEndpointMixinBase(StackExchangeAPIEndpoint):
    def __new__(cls, *args, **kwargs):
        if cls is StackExchangeAPIPartialEndpointMixinBase:
            raise TypeError(
                'Cannot directly instantiate {} class.'.format(
                    cls.__name__
                )
            )

        if six.PY3:
            return super(
                StackExchangeAPIPartialEndpointMixinBase,
                cls
            ).__new__(cls)
        else:
            return super(
                StackExchangeAPIPartialEndpointMixinBase,
                cls
            ).__new__(cls, *args, **kwargs)


class Undoable(StackExchangeAPIPartialEndpointMixinBase):
    def undo(self, name, reverse=False):
        path = name
        if reverse:
            path += '/undo'
        return self.extend_with(name=path, offset=3, writable=True)


class Comments(StackExchangeAPIPartialEndpointMixinBase):
    def comments(self, **kwargs):
        parameters = {
            'name': 'comments',
            'offset': 3
        }
        parameters.update(kwargs)
        return self.extend_with(**parameters)


class Filtered(StackExchangeAPIPartialEndpointMixinBase):
    def in_(self, *items, **kwargs):
        """
        Provide item filtering for ids, tags, access tokens etc
        """
        items = map(str, items or kwargs.get('items', []))
        writable = kwargs.get('writable', False)
        return self.extend_with(name=','.join(items), offset=2,
                                writable=writable)


class Vote(Undoable):
    def up_vote(self, undo=False):
        return self.undo(name='upvote', reverse=undo)

    def down_vote(self, undo=False):
        return self.undo(name='downvote', reverse=undo)


class CreateUpdateDelete(StackExchangeAPIPartialEndpointMixinBase):
    def add(self):
        return self.extend_with(name='add', offset=4, writable=True)

    def edit(self):
        return self.extend_with(name='edit', offset=3, writable=True)

    def delete(self):
        return self.extend_with(name='delete', offset=3, writable=True)


class Accept(Undoable):
    def accept(self, undo=False):
        return self.undo('accept', reverse=undo)


class Flags(StackExchangeAPIPartialEndpointMixinBase):
    def add(self):
        return self.extend_with(name='flags/add', offset=3, writable=True)

    def options(self):
        return self.extend_with(name='flags/options', offset=3)


class Favorite(Undoable):
    def favorite(self, undo=False):
        self.undo('favorite', reverse=undo)
