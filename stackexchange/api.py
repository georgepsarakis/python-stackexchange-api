from time import time, sleep
import urlparse
import requests
from requests import Request
from http import StackExchangeAPIResponse


class StackExchangeAPI(object):
    _BASE_URL = 'https://api.stackexchange.com'
    _AVAILABLE_VERSIONS = ('2.1', '2.2')

    def __init__(self, version=None, auth=None):
        self._last_response = None
        self._version = version or self._AVAILABLE_VERSIONS[-1]
        self._base_url = '{}/{}'.format(self._BASE_URL, self._version)
        self._last_request = None
        self._back_off_timestamp = None
        self._auth = auth

    @property
    def version(self):
        return self._version

    @version.setter
    def version(self, value):
        if value not in self._AVAILABLE_VERSIONS:
            raise ValueError
        self._version = value
        self._base_url = '{}/{}'.format(self._BASE_URL, self._version)

    def _build_http_request(self, request, data=None):
        method, path, parameters = request.compile()
        url = urlparse.urljoin(self._base_url, path.compile())
        return Request(
            method=method,
            url=url,
            params=parameters,
            data=data,
            auth=self._auth
        )

    def fetch(self, request):
        """
        :param StackExchangeAPIRequest request:
        """
        self._last_request = request
        http_request = self._build_http_request(request)
        prepared_request = http_request.prepare()
        now = time()
        if now < self._back_off_timestamp:
            sleep(self._back_off_timestamp - now)
        with requests.Session() as session:
            response = session.send(prepared_request)
        self._back_off_timestamp = time()
        response = StackExchangeAPIResponse(request, response)
        if not response.is_error():
            self._back_off_timestamp += response.json.get('backoff', 0)
        self._last_response = response
        return response

    def fetch_next_page(self):
        """
        :rtype: StackExchangeAPIResponse
        """
        return self.fetch(
            request=self._last_request.with_next(name='page')
        )

    def request(self):
        """
        :rtype: StackExchangeAPIRequest
        """
        from http import StackExchangeAPIRequest
        return StackExchangeAPIRequest(api=self)
