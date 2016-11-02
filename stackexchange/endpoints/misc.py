from stackexchange.path import StackExchangeAPISubEndpoint


class Undoable(StackExchangeAPISubEndpoint):
    def undoable_action(self, name, undo=False):
        self.extend_path(3, name, writable=True)
        if undo:
            self.extend_path(4, 'undo')
        return self


class Comments(StackExchangeAPISubEndpoint):
    def comments(self, **kwargs):
        parameters = {
            'name': 'comments',
            'position': 3
        }
        parameters.update(kwargs)
        return self.extend_path(**parameters)


class Filtered(StackExchangeAPISubEndpoint):
    def filter(self, *items, **kwargs):
        """
        Provide item filtering for ids, tags, access tokens etc
        """
        items = map(str, items)
        return self.extend_path(position=2, name=','.join(items), **kwargs)


class UpVote(Undoable):
    def up_vote(self, undo=False):
        return self.undoable_action('upvote', undo=undo)


class DownVote(Undoable):
    def down_vote(self, undo=False):
        return self.undoable_action('downvote', undo=undo)


class CreateUpdateDelete(StackExchangeAPISubEndpoint):
    def add(self):
        return self.extend_path(position=4, name='add', writable=True)

    def edit(self):
        return self.extend_path(position=3, name='edit', writable=True)

    def delete(self):
        return self.extend_path(position=3, name='delete', writable=True)


class Accept(Undoable):
    def accept(self, undo=False):
        return self.undoable_action('accept', undo=undo)


class Flags(StackExchangeAPISubEndpoint):
    @property
    def flags(self):
        new_instance = Flags(self._path)
        new_instance.path.add_segment(3, 'flags')
        return new_instance

    def add(self):
        new_instance = self.extend_path(position=3, name='flags')
        return new_instance.extend_path(position=4, name='add', writable=True)

    def options(self):
        new_instance = self.extend_path(position=3, name='flags')
        return new_instance.extend_path(position=4, name='options')


class Favorite(Undoable):
    def favorite(self, undo=False):
        self.undoable_action('favorite', undo=undo)
