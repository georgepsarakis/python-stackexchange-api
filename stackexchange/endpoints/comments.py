from stackexchange.endpoints.mixins import Flags, Vote, CreateUpdateDelete


class Comments(Flags, CreateUpdateDelete, Vote):
    pass
