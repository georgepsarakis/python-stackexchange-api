from stackexchange.endpoints.mixins import Filtered


class Badges(Filtered):
    def name(self):
        return self.extend_with(name='name', offset=2)

    def recipients(self):
        return self.extend_with(name='recipients', offset=3)
