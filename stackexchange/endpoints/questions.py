from stackexchange.path import StackExchangeAPIEndpoint
from stackexchange.endpoints.mixins import Flags, CreateUpdateDelete, \
    Vote, Accept, Favorite, Filtered


class Questions(
    StackExchangeAPIEndpoint,
    Filtered,
    Flags,
    CreateUpdateDelete,
    Accept,
    Vote,
    Favorite
):
    def featured(self):
        return self.extend_path(position=2, name='featured')

    def close_options(self):
        return self.extend_path(
            position=3,
            name='close/options',
            writable=True
        )

    def add(self):
        if self.path.last_segment == 'answers':
            position = 4
        else:
            position = 2
        return self.extend_path(position=position, name='add')

    def no_answers(self):
        return self.extend_path(position=2, name='no-answers')

    def render(self):
        if self.path.last_segment == 'answers':
            position = 4
        else:
            position = 2
        return self.extend_path(position=position, name='render')

    def unanswered(self, my_tags=False):
        if not my_tags:
            return self.extend_path(position=2, name='unanswered')
        else:
            return self.extend_path(
                position=2,
                name='unanswered'
            ).extend_path(
                position=3,
                name='my-tags'
            )

    def timeline(self):
        return self.extend_path(position=3, name='timeline')

    def answers(self):
        return self.extend_path(position=3, name='answers')

    def linked(self):
        return self.extend_path(position=3, name='linked')

    def related(self):
        return self.extend_path(position=3, name='related')
