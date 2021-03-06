import urllib

from flask import json

from base import BaseTest


class SuggestTestCase(BaseTest):
    def setUp(self):
        super(SuggestTestCase, self).setUp()

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

    def test_keywords_status(self):
        requst = "/suggest/keywords?q=" + urllib.quote_plus(self.query)
        response = self.client.get(requst)

        self.assertFalse(response is None)
        self.assertEquals(response.status_code, 200)

    def test_autocomplete_bad_request(self):
        request = "/suggest/autocomplete"
        response = self.client.get(request)

        self.assertEqual(response.status_code, 400)

    def test_keywords_bad_request(self):
        request = "/suggest/keywords"
        response = self.client.get(request)

        self.assertEqual(response.status_code, 400)

    def test_autocomplete_data_contains_keys(self):
        request = "/suggest/autocomplete?q=" + urllib.quote_plus(self.query)
        response = self.client.get(request)
        data = response.data

        self.assertFalse(data is None)
        self.assertTrue(isinstance(data, str))

        json_data = json.loads(data)
        self.assertFalse(json_data is None)
        self.assertTrue(isinstance(json_data, dict))

        self.assertTrue("suggestions" in json_data)

    def test_keywords_data_count(self):
        count = 10
        request = "/suggest/keywords?q=" + \
                  urllib.quote_plus(self.query) + "&top_n=%d" % count
        response = self.client.get(request)
        data = response.data

        self.assertFalse(data is None)
        self.assertTrue(isinstance(data, str))

        json_data = json.loads(data)
        self.assertFalse(json_data is None)
        self.assertTrue(isinstance(json_data, dict))

        self.assertTrue("keywords" in json_data)
        self.assertTrue(len(json_data["keywords"]) > 0)
        self.assertEquals(len(json_data["keywords"]), count)

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
