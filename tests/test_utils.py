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


if __name__ == "__main__":
    unittest.main(verbosity=2)
