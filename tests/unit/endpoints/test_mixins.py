import unittest

from stackexchange.endpoints import mixins


class TestStackExchangeAPIPartialEndpointMixinBase(unittest.TestCase):
    def test_direct_instantiation_error(self):
        with self.assertRaises(TypeError):
            mixins.StackExchangeAPIPartialEndpointMixinBase()

        class Test(mixins.StackExchangeAPIPartialEndpointMixinBase):
            pass

        self.assertIsInstance(
            Test(),
            mixins.StackExchangeAPIPartialEndpointMixinBase
        )

