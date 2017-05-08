from stackexchange.path import StackExchangeAPIEndpoint


class Search(StackExchangeAPIEndpoint):
    def similar(self):
        return self.extend_with(name='similar', offset=1)

    def excerpts(self):
        return self.extend_with(name='excerpts', offset=2)

    def advanced(self):
        return self.extend_with(name='advanced', offset=2)
