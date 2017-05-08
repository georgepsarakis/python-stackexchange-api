from collections import Mapping
import json

import six


def serialize(obj, **kwargs):
    dumps_kwargs = {
        'indent': 4
    }
    dumps_kwargs.update(kwargs)
    return json.dumps(obj, cls=ModelSerializer, **dumps_kwargs)


class ModelSerializer(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, Model):
            return o.to_native()
        return super(ModelSerializer, self).default(o)


class Model(Mapping):
    def __init__(self, data):
        self.__data = self._transform(data, self._transform_to_model)

    @staticmethod
    def _transform_to_model(value):
        if isinstance(value, (list, dict)):
            value = Model(value)
        return value

    @staticmethod
    def _transform_to_native(value):
        if isinstance(value, Model):
            value = value.to_native()
        return value

    @staticmethod
    def _transform(data, value_function):
        container = None
        iterator = None

        if isinstance(data, list):
            iterator = enumerate(data)
            container = [None] * len(data)
        elif isinstance(data, dict):
            iterator = six.iteritems(data)
            container = {}

        if container is not None:
            for key, value in iterator:
                container[key] = value_function(value)
            return container
        else:
            return data

    def to_native(self):
        return self._transform(self.__data, self._transform_to_native)

    def __getitem__(self, key):
        return self.__data[key]

    def __len__(self):
        return len(self.__data)

    def __iter__(self):
        return self.__data.__iter__()

    def __repr__(self):
        return '<{}:{}:({})>'.format(
            self.__class__.__name__,
            str(hex(id(self))),
            serialize(self.to_native())
        )
