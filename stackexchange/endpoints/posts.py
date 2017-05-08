from stackexchange.endpoints.mixins import Filtered, Comments


class Posts(Filtered, Comments):
    def add(self):
        return self.extend_with(name='add', offset=4, writable=True)

    def render(self):
        return self.extend_with(name='render', offset=4)

    def revisions(self):
        return self.extend_with(name='revisions', offset=3)

    def suggested_edits(self):
        return self.extend_with(name='suggested-edits', offset=3)
