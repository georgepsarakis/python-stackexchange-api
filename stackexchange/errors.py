class StackExchangeInvalidAPIMethodError(Exception):
    pass


class StackExchangeInvalidEndpointPathError(Exception):
    pass


class StackExchangeAPIError(Exception):
    def __init__(self, response):
        self.response = response
