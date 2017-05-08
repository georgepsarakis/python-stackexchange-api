from stackexchange.endpoints.mixins import Flags, CreateUpdateDelete, \
    Vote, Accept, Favorite, Filtered


class Questions(Filtered, Flags, CreateUpdateDelete, Accept, Vote, Favorite):
    def featured(self):
        return self.extend_with(name='featured', offset=2)

    def close_options(self):
        return self.extend_with(name='close/options', offset=3, writable=True)

    def add(self):
        if self.path.endswith('answers'):
            position = 4
        else:
            position = 2
        return self.extend_with(name='add', offset=position)

    def no_answers(self):
        return self.extend_with(name='no-answers', offset=2)

    def render(self):
        if self.path.endswith('answers'):
            position = 4
        else:
            position = 2
        return self.extend_with(name='render', offset=position)

    def unanswered(self, my_tags=False):
        if not my_tags:
            return self.extend_with(name='unanswered', offset=2)
        else:
            return self.extend_with(name='unanswered', offset=2).extend_with(
                name='my-tags', offset=3)

    def timeline(self):
        return self.extend_with(name='timeline', offset=3)

    def answers(self):
        return self.extend_with(name='answers', offset=3)

    def linked(self):
        return self.extend_with(name='linked', offset=3)

    def related(self):
        return self.extend_with(name='related', offset=3)
