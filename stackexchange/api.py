from functools import wraps
from inspect import isclass
from time import time, sleep
import requests
from requests import Request
from retrying import retry
from six.moves.urllib.parse import urljoin
from stackexchange.http import StackExchangeAPIResponse


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

    def maybe_wait(self):
        now = time()
        should_wait = now < self._next_request_min_timestamp
        if should_wait:
            wait = self._next_request_min_timestamp - now
            sleep(wait)
            return True
        return False

    def retryable(self, function):
        @wraps(function)
        def wrapper(*args, **kwargs):
            self.maybe_wait()
            response = function(*args, **kwargs)
            backoff_interval = response.data.get('backoff', 0)
            self.set_next_request_minimum_time(backoff_interval)
            return response
        return retry(
            retry_on_exception=BackoffStrategy._retry_on_throttle_error,
            **self._retry_kwargs
        )(wrapper)


class Paginator(object):
    def __init__(self, request):
        self._request = request

    def __iter__(self):
        initial_iteration = True
        response = self._request.fetch()
        while response.has_more() or initial_iteration:
            yield self._request.fetch()
            initial_iteration = False
            self._request = self._request.next_('page')


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

    def _prepare_http_request(self, request, **kwargs):
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

    def fetch(self, request, request_kwargs=None, session=None):
        """
        :param StackExchangeAPIRequest request:
        """
        current_request_kwargs = self._default_request_kwargs.copy()
        current_request_kwargs.update(request_kwargs or {})
        session = session or self._default_http_session

        http_request = self._prepare_http_request(
            request,
            **current_request_kwargs
        )

        with session or requests.Session() as session:
            api_response = session.send(http_request.prepare())

        response = StackExchangeAPIResponse(request, api_response)
        self._last_request = request
        return response

    def request(self):
        """
        :rtype: StackExchangeAPIRequest
        """
        from stackexchange.http import StackExchangeAPIRequest
        return StackExchangeAPIRequest(api=self)
