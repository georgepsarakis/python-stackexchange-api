from stackexchange.path import StackExchangeAPIEndpoint
from stackexchange.endpoints.misc import (
    Flags,
    Accept,
    CreateUpdateDelete,
    UpVote,
    DownVote,
    Comments,
    Filtered
)


class Answers(
    StackExchangeAPIEndpoint,
    Flags,
    Accept,
    CreateUpdateDelete,
    UpVote,
    DownVote,
    Comments,
    Filtered
):
    def questions(self):
        return self.extend_path(name='questions', position=3)
