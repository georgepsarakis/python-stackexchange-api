from stackexchange.path import StackExchangeAPIEndpoint
from stackexchange.endpoints.misc import Flags, UpVote, CreateUpdateDelete


class Comments(StackExchangeAPIEndpoint, Flags, CreateUpdateDelete, UpVote):
    pass
