import unittest
from stackexchange.utils import Model


class TestUtilsModel(unittest.TestCase):
    def test_to_native(self):
        fixture = {
            'a': {
                'b': [1, {'c': 'd'}]
            }
        }
        model_fixture = Model(fixture)
        self.assertDictEqual(model_fixture.to_native(), fixture)

    def test_getitem(self):
        m = Model({
            'k1': {
                'k2': [1, 2, 3]
            }
        })
        self.assertListEqual(
            list(m['k1']['k2']),
            [1, 2, 3]
        )

        m = Model([
            {'a': {'b': 1, 'c': [1, 2]}}
        ])
        self.assertEqual(m[0]['a']['b'], 1)
