from stackexchange.path import StackExchangeAPIEndpoint
from stackexchange.endpoints.mixins import (
    Flags,
    Accept,
    CreateUpdateDelete,
    Vote,
    Comments,
    Filtered
)


class Answers(
    StackExchangeAPIEndpoint,
    Flags,
    Accept,
    CreateUpdateDelete,
    Vote,
    Comments,
    Filtered
):
    def questions(self):
        return self.extend_path(name='questions', position=3)
