from time import time, sleep
import requests
from requests import Request
from retrying import retry
from six.moves.urllib.parse import urljoin
from .http import StackExchangeAPIResponse


class BackoffStrategy(object):
    @staticmethod
    def retry_on_fetch_error(exception):
        if not hasattr(exception, 'response'):
            return False
        if exception.response.data['error_id'] == 502:
            return True
        return False


class StackExchangeAPI(object):
    _BASE_URL = 'https://api.stackexchange.com'
    _AVAILABLE_VERSIONS = ('2.1', '2.2')

    def __init__(
        self,
        version=None,
        auth=None,
        http_session=None,
        request_kwargs=None
    ):
        self._last_response = None
        self._version = version or self._AVAILABLE_VERSIONS[-1]
        self._base_url = '{}/{}'.format(self._BASE_URL, self._version)
        self._last_request = None
        self._back_off_timestamp = None
        self._auth = auth
        self._default_request_kwargs = request_kwargs or {}
        self._default_http_session = http_session or None

    @property
    def version(self):
        return self._version

    @version.setter
    def version(self, value):
        if value not in self._AVAILABLE_VERSIONS:
            raise ValueError
        self._version = value
        self._base_url = '{}/{}'.format(self._BASE_URL, self._version)

    def _build_http_request(self, request, **kwargs):
        method, path, parameters = request.compile()
        if path is None:
            url = self._base_url
        else:
            url = urljoin(self._base_url, path.compile())
        request_kwargs = dict(
            method=method,
            url=url,
            params=parameters,
            auth=self._auth
        )
        request_kwargs.update(kwargs)
        return Request(**request_kwargs)

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

    @retry(
        retry_on_exception=BackoffStrategy.retry_on_fetch_error,
        wait_random_min=10**4
    )
    def fetch(self, request, request_kwargs=None, session=None):
        """
        :param StackExchangeAPIRequest request:
        """
        default_request_kwargs = self._default_request_kwargs.copy()
        default_request_kwargs.update(request_kwargs or {})
        request_kwargs = default_request_kwargs
        session = session or self._default_http_session

        self._should_backoff()
        http_request = self._build_http_request(request, **request_kwargs)
        if session is None:
            with requests.Session() as session:
                http_response = session.send(http_request.prepare())
        else:
            http_response = session.send(http_request.prepare())
        self._back_off_timestamp = time()
        response = StackExchangeAPIResponse(request, http_response)
        self._back_off_timestamp += response.data.get('backoff', 0)
        self._last_request = request
        self._last_response = response
        return response

    def fetch_next_page(self, **kwargs):
        """
        :rtype: StackExchangeAPIResponse
        """
        return self.fetch(
            request=self._last_request.next_(name='page'),
            **kwargs
        )

    def request(self):
        """
        :rtype: StackExchangeAPIRequest
        """
        from .http import StackExchangeAPIRequest
        return StackExchangeAPIRequest(api=self)
