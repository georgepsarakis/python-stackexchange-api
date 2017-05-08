from stackexchange.endpoints.mixins import (
    Flags,
    Accept,
    CreateUpdateDelete,
    Vote,
    Comments,
    Filtered
)


class Answers(
    Flags,
    Accept,
    CreateUpdateDelete,
    Vote,
    Comments,
    Filtered
):
    def questions(self):
        return self.extend_with(name='questions', offset=3)
