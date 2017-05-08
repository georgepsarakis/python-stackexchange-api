from stackexchange.endpoints.mixins import Filtered


class Tags(Filtered):
    def info(self):
        return self.extend_with(name='info', offset=3)

    def faq(self):
        return self.extend_with(name='faq', offset=3)

    def related(self):
        return self.extend_with(name='related', offset=3)

    def wikis(self):
        return self.extend_with(name='wikis', offset=3)

    def top_answerers(self, period):
        name = 'top-answerers/{}'.format(period)
        return self.extend_with(name=name, offset=3)

    def top_askers(self, period):
        name = 'top-askers/{}'.format(period)
        return self.extend_with(name=name, offset=3)

    def moderator_only(self):
        return self.extend_with(name='moderator-only', offset=2)

    def required(self):
        return self.extend_with(name='required', offset=2)

    def synonyms(self):
        if self.path.endswith('tags'):
            return self.extend_with(name='synonyms', offset=2)
        else:
            return self.extend_with(name='synonyms', offset=3)
