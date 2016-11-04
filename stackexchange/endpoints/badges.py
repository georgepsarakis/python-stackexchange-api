from stackexchange.path import StackExchangeAPIEndpoint
from stackexchange.endpoints.misc import Filtered


class Badges(StackExchangeAPIEndpoint, Filtered):
    def name(self):
        return self.extend_path(position=2, name='name')

    def recipients(self):
        return self.extend_path(position=3, name='recipients')
