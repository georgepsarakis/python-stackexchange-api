from copy import deepcopy, copy
import json
from collections import Mapping


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
        container = None
        if isinstance(data, list):
            iterator = enumerate(data)
            container = [None] * len(data)
        elif isinstance(data, dict):
            iterator = data.items()
            container = {}

        if container is not None:
            for key, value in iterator:
                if isinstance(value, (list, dict)):
                    value = Model(value)
                container[key] = value

        self.__data = container

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

    def to_native(self):

        if isinstance(self.__data, list):
            container = [None] * len(self.__data)
            iterator = enumerate(self.__data)
        else:
            container = {}
            iterator = self.__data.iteritems()

        for index, item in iterator:
            if isinstance(item, Model):
                item = item.to_native()
            container[index] = item

        return container


if __name__ == "__main__":
    a = {
        'k1': {
            'b1': [1, 2, 3]
        }
    }
    model_a = Model(a)

    print model_a
    print model_a['k1']['b1']
    b = [
        {'a': {'b': 1, 'c': [1, 2]}}
    ]
    model_b = Model(b)
    print model_b
    print model_b[0]['a']['b']
    print model_b.to_native()
    print Model({'a': {'b': {'c': [1]}}}).to_native()
