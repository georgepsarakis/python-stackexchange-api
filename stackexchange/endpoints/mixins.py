from stackexchange.path import StackExchangeAPIURLPath


class StackExchangeAPIURLPathMixinBase(StackExchangeAPIURLPath):
    def __new__(cls, *args, **kwargs):
        if cls is StackExchangeAPIURLPathMixinBase:
            raise NotImplementedError(
                'Cannot directly instantiate {} class'.format(
                    cls.__name__
                )
            )
        return super(StackExchangeAPIURLPathMixinBase, cls).__new__(
            cls,
            *args,
            **kwargs
        )


class Undo(StackExchangeAPIURLPathMixinBase):
    def undo(self, name, reverse=False):
        path = name
        if reverse:
            path += '/undo'
        return self.extend_path(name=path, position=3, writable=True)


class Comments(StackExchangeAPIURLPathMixinBase):
    def comments(self, **kwargs):
        parameters = {
            'name': 'comments',
            'position': 3
        }
        parameters.update(kwargs)
        return self.extend_path(**parameters)


class Filtered(StackExchangeAPIURLPathMixinBase):
    def in_(self, *items, **kwargs):
        """
        Provide item filtering for ids, tags, access tokens etc
        """
        items = map(str, items)
        return self.extend_path(position=2, name=','.join(items), **kwargs)


class Vote(Undo):
    def up_vote(self, undo=False):
        return self.undo('upvote', reverse=undo)

    def down_vote(self, undo=False):
        return self.undo('downvote', reverse=undo)


class CreateUpdateDelete(StackExchangeAPIURLPathMixinBase):
    def add(self):
        return self.extend_path(position=4, name='add', writable=True)

    def edit(self):
        return self.extend_path(position=3, name='edit', writable=True)

    def delete(self):
        return self.extend_path(position=3, name='delete', writable=True)


class Accept(Undo):
    def accept(self, undo=False):
        return self.undo('accept', reverse=undo)


class Flags(StackExchangeAPIURLPathMixinBase):
    def add(self):
        return self.extend_path(position=3, name='flags/add', writable=True)

    def options(self):
        return self.extend_path(position=3, name='flags/options')


class Favorite(Undo):
    def favorite(self, undo=False):
        self.undo('favorite', reverse=undo)
