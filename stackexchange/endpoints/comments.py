from stackexchange.path import StackExchangeAPIEndpoint
from stackexchange.endpoints.mixins import Flags, Vote, CreateUpdateDelete


class Comments(StackExchangeAPIEndpoint, Flags, CreateUpdateDelete, Vote):
    pass
