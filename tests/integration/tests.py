import unittest
from stackexchange import StackExchangeAPI
from stackexchange.endpoints.answers import Answers

import warnings
warnings.filterwarnings("ignore")


class IntegrationTests(unittest.TestCase):
    def setUp(self):
        self.api = StackExchangeAPI()
        self.so_request = self.api.request().site('stackoverflow')

    def test_fetch_answer_comments(self):
        comments_endpoint = Answers().in_(40314706).comments()
        response = self.so_request.using(comments_endpoint).fetch()
        self.assertGreater(len(response.json['items']), 0)

    def test_slice(self):
        total_items = 0
        for response in self.so_request.using(Answers()).pagesize(1)[1:4]:
            self.assertIn('answer_id', response.json['items'][0])
            total_items += len(response.json['items'])
        self.assertEqual(total_items, 3)
