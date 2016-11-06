from inspect import isclass
from time import time, sleep
import requests
from requests import Request
from retrying import retry
from six.moves.urllib.parse import urljoin
from .http import StackExchangeAPIResponse


class BackoffStrategy(object):
    def __init__(self, **kwargs):
        default_retry_parameters = dict(
            wait_random_min=10**4,
            wait_random_max=3*10**4,
            stop_max_attempt_number=10
        )
        default_retry_parameters.update(kwargs)
        self._retry_kwargs = default_retry_parameters
        self._next_request_min_timestamp = time()

    @staticmethod
    def _retry_on_throttle_error(exception):
        if not hasattr(exception, 'response'):
            return False
        if exception.response.data['error_id'] == 502:
            return True
        return False

    def set_next_request_minimum_time(self, backoff_interval):
        self._next_request_min_timestamp = time() + backoff_interval

    def wait(self):
        now = time()
        should_wait = now < self._next_request_min_timestamp
        if should_wait:
            wait = self._next_request_min_timestamp - now
            sleep(wait)
            return True
        return False

    def retryable(self, function):
        return retry(
            retry_on_exception=BackoffStrategy._retry_on_throttle_error,
            **self._retry_kwargs
        )(function)


class StackExchangeAPI(object):
    _BASE_URL = 'https://api.stackexchange.com'
    _AVAILABLE_VERSIONS = ('2.1', '2.2')

    def __init__(
        self,
        version=None,
        auth=None,
        http_session=None,
        http_request_kwargs=None,
        throttle_strategy=BackoffStrategy
    ):
        self._last_response = None
        self._version = version or self._AVAILABLE_VERSIONS[-1]
        self._base_url = '{}/{}'.format(self._BASE_URL, self._version)
        self._last_request = None
        self._back_off_timestamp = None
        self._auth = auth
        self._default_request_kwargs = http_request_kwargs or {}
        self._default_http_session = http_session or None
        if isclass(throttle_strategy):
            throttle_strategy = throttle_strategy()
        self._back_off_strategy = throttle_strategy
        self.fetch = self._back_off_strategy.retryable(self.fetch)

    @property
    def backoff_strategy(self):
        return self._back_off_strategy

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
        request_kwargs.update(self._default_request_kwargs)
        request_kwargs.update(kwargs)
        return Request(**request_kwargs)

    def get_http_request(self, request):
        """
        :param StackExchangeAPIRequest request:
        :rtype: requests.Request
        """
        return self._build_http_request(request)

    def fetch(self, request, request_kwargs=None, session=None):
        """
        :param StackExchangeAPIRequest request:
        """
        default_request_kwargs = self._default_request_kwargs.copy()
        default_request_kwargs.update(request_kwargs or {})
        request_kwargs = default_request_kwargs
        session = session or self._default_http_session

        self.backoff_strategy.wait()
        http_request = self._build_http_request(request, **request_kwargs)

        if session is None:
            with requests.Session() as session:
                http_response = session.send(http_request.prepare())
        else:
            http_response = session.send(http_request.prepare())

        response = StackExchangeAPIResponse(request, http_response)
        backoff_interval = response.data.get('backoff', 0)

        self.backoff_strategy.set_next_request_minimum_time(backoff_interval)
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
