from stackexchange.path import StackExchangeAPIEndpoint
from stackexchange.endpoints.mixins import Filtered


class Errors(StackExchangeAPIEndpoint, Filtered):
    pass
