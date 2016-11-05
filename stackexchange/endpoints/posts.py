from stackexchange.path import StackExchangeAPIEndpoint
from stackexchange.endpoints.mixins import Filtered, Comments


class Posts(StackExchangeAPIEndpoint, Filtered, Comments):
    def add(self):
        return self.extend_path(name='add', position=4, writable=True)

    def render(self):
        return self.extend_path(name='render', position=4)

    def revisions(self):
        return self.extend_path(name='revisions', position=3)

    def suggested_edits(self):
        return self.extend_path(name='suggested-edits', position=3)
