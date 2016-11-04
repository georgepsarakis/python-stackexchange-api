from time import time, sleep
import requests
from requests import Request
from six.moves.urllib.parse import urljoin
from .http import StackExchangeAPIResponse


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
        if path is None:
            url = self._base_url
        else:
            url = urljoin(self._base_url, path.compile())
        return Request(
            method=method,
            url=url,
            params=parameters,
            data=data,
            auth=self._auth
        )

    def get_http_request(self, request):
        """
        :param StackExchangeAPIRequest request:
        :rtype: requests.Request
        """
        return self._build_http_request(request)

    def _should_backoff(self):
        now = time()
        should_wait = (
            self._back_off_timestamp is not None and
            now < self._back_off_timestamp
        )
        if should_wait:
            wait = self._back_off_timestamp - now
            sleep(wait)
            return True
        return False

    def fetch(self, request):
        """
        :param StackExchangeAPIRequest request:
        """
        self._should_backoff()
        http_request = self._build_http_request(request)
        with requests.Session() as session:
            response = session.send(http_request.prepare())
        self._back_off_timestamp = time()
        response = StackExchangeAPIResponse(request, response)
        if not response.is_error():
            self._back_off_timestamp += response.json.get('backoff', 0)
        self._last_request = request
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
        from .http import StackExchangeAPIRequest
        return StackExchangeAPIRequest(api=self)
