from calendar import timegm
from copy import copy, deepcopy
from uuid import uuid4
from utils import Model, serialize


class StackExchangeAPIRequest(object):
    def __init__(self, endpoint=None, api=None):
        self._api = api
        self._parameters = []
        self._endpoint = endpoint

    def __repr__(self):
        return '<{}:{} [{}]/[{}]>'.format(
            self.__class__.__name__,
            str(hex(id(self))),
            self._endpoint,
            self.parameters
        )

    @property
    def parameters(self):
        return dict(self._parameters)

    def __copy__(self):
        new_instance = StackExchangeAPIRequest(self._endpoint)
        new_instance._parameters = copy(self._parameters)
        new_instance._api = self._api
        return new_instance

    def filter_by(self, name, value, may_be_callable=True):
        if may_be_callable:
            if callable(value):
                value = value()
        value = str(value)
        self._parameters.append((name, value))
        return copy(self)

    def with_next(self, name, amount=1, initial=1):
        parameter_dict = dict(self._parameters)
        if name not in parameter_dict:
            parameter_dict[name] = initial
        parameter_dict[name] = initial + amount
        return self.filter_by(name, parameter_dict[name])

    def page(self, number):
        return self.filter_by('page', number)

    def pagesize(self, number):
        return self.filter_by('pagesize', number)

    def request_id(self, identifier=uuid4):
        return self.filter_by('request_id', identifier)

    def access_token(self, token):
        return self.filter_by('token', token)

    def key(self, application_key):
        return self.filter_by('key', application_key)

    def order_by(self, *fields):
        return self.filter_by('sort', ','.join(fields))

    def from_date(self, start_date):
        return self.filter_by('fromdate', timegm(start_date.timetuple()))

    def to_date(self, end_date):
        return self.filter_by('todate', timegm(end_date.timetuple()))

    def compile(self):
        parameters = {name: value for name, value in self._parameters}
        if self._endpoint is None:
            return None, None, parameters
        return self._endpoint.http_method, self._endpoint.path, parameters

    def using(self, endpoint):
        """
        :rtype: StackExchangeAPIRequest
        """
        new_instance = copy(self)
        new_instance._endpoint = endpoint
        return new_instance

    def fetch(self):
        """
        :rtype: StackExchangeAPIResponse
        """
        return self._api.fetch(self)

    def __getitem__(self, item):
        if not isinstance(item, slice):
            raise TypeError
        for page in xrange(item.start, item.stop, item.step or 1):
            yield self.filter_by(name='page', value=page).fetch()

    def __iter__(self):
        initial_iteration = True
        response = self.fetch()
        while response.has_more() or initial_iteration:
            initial_iteration = False
            yield response
            response = self.with_next('page').fetch()


class StackExchangeAPIResponse(object):
    def __init__(self, request, response):
        self._request = request
        self._response = response
        self._status_code = self._response.status_code
        self._json_content = response.json()
        self.data = Model(self._json_content)

    @property
    def request(self):
        """
        :rtype: StackExchangeAPIRequest
        """
        return self._request

    def is_error(self):
        return 'error_id' in self.json

    def has_more(self):
        response_data = self.json
        return 'has_more' in response_data and response_data['has_more']

    @property
    def items(self):
        return self.json.get('items', list())

    @property
    def json(self):
        return deepcopy(self._json_content)

    def __repr__(self):
        return '<{}@{}:({})>'.format(
            self.__class__.__name__,
            str(hex(id(self))),
            serialize(self.json, indent=4)
        )

    __str__ = __repr__
