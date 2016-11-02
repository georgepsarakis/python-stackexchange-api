from stackexchange.path import StackExchangeAPIEndpoint


class Search(StackExchangeAPIEndpoint):
    def similar(self):
        return self.extend_path(name='similar', position=1)

    def excerpts(self):
        return self.extend_path(name='excerpts', position=2)

    def advanced(self):
        return self.extend_path(name='advanced', position=2)
