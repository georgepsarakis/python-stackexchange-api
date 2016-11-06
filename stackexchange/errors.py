class StackExchangeInvalidAPIMethodError(Exception):
    pass


class StackExchangeInvalidEndpointPathError(Exception):
    pass


class StackExchangeAPIError(Exception):
    def __init__(self, message, response):
        self.response = response
        super(StackExchangeAPIError, self).__init__(message)
