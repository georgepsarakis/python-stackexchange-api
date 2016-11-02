from requests.auth import AuthBase


class StackExchangeAPIAuth(AuthBase):
    def __init__(self, key, access_token):
        super(StackExchangeAPIAuth, self).__init__()
        self._key = key
        self._access_token = access_token

    def __call__(self, request):
        request.params.update({
            'key': self._key,
            'access_token': self._access_token
        })




