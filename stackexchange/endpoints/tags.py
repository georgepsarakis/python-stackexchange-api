from stackexchange.path import StackExchangeAPIEndpoint
from stackexchange.endpoints.mixins import Filtered


class Tags(StackExchangeAPIEndpoint, Filtered):
    def info(self):
        return self.extend_path(name='info', position=3)

    def faq(self):
        return self.extend_path(name='faq', position=3)

    def related(self):
        return self.extend_path(name='related', position=3)

    def wikis(self):
        return self.extend_path(name='wikis', position=3)

    def top_answerers(self, period):
        name = 'top-answerers/{}'.format(period)
        return self.extend_path(name=name, position=3)

    def top_askers(self, period):
        name = 'top-askers/{}'.format(period)
        return self.extend_path(name=name, position=3)

    def moderator_only(self):
        return self.extend_path(name='moderator-only', position=2)

    def required(self):
        return self.extend_path(name='required', position=2)

    def synonyms(self):
        if self.path.last_segment == 'tags':
            return self.extend_path(name='synonyms', position=2)
        else:
            return self.extend_path(name='synonyms', position=3)
