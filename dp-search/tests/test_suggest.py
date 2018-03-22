import unittest

import urllib

from flask import json

# Nosetests will take care of sys.path for this import
from server.app import create_app
app = create_app()


class SuggestTestCase(unittest.TestCase):
    def setUp(self):
        self.app = app
        self.app_context = self.app.app_context()
        self.app_context.push()
        self.client = self.app.test_client()

        self.query = "rpj chi"
        self.tokens = self.query.split()
        self.expected_tokens = ["rpi", "cpi"]

    def tearDown(self):
        self.app_context.pop()

    def test_autocomplete_status(self):
        request = "/suggest/autocomplete?q=" + urllib.quote_plus(self.query)
        response = self.client.get(request)

        self.assertFalse(response is None)
        self.assertEqual(response.status_code, 200)

    def test_autocomplete_data_contains_keys(self):
        request = "/suggest/autocomplete?q=" + urllib.quote_plus(self.query)
        response = self.client.get(request)
        data = response.data

        self.assertFalse(data is None)
        self.assertTrue(isinstance(data, str))

        json_data = json.loads(data)
        self.assertFalse(json_data is None)
        self.assertTrue(isinstance(json_data, dict))

        self.assertTrue("keywords" in json_data)
        self.assertTrue("suggestions" in json_data)

        self.assertTrue(len(json_data["keywords"]) > 0)

    def test_autocomplete_options(self):
        request = "/suggest/autocomplete?q=" + urllib.quote_plus(self.query)
        response = self.client.get(request)
        data = response.data

        self.assertFalse(data is None)
        self.assertTrue(isinstance(data, str))

        json_data = json.loads(data)
        self.assertFalse(json_data is None)
        self.assertTrue(isinstance(json_data, dict))

        available_suggestions = json_data["suggestions"]
        for token, expected in zip(self.tokens, self.expected_tokens):
            self.assertTrue(token in available_suggestions)
            suggestions = available_suggestions[token]
            self.assertTrue("suggestions" in suggestions)
            self.assertTrue(len(suggestions["suggestions"]) > 0)
            suggestion = suggestions["suggestions"][0]
            self.assertTrue(suggestion["confidence"] > 0.95)
            self.assertEquals(suggestion["suggestion"], expected)
