import urllib

from flask import json

from base import BaseTest


class SearchTestCase(BaseTest):
    def setUp(self):
        super(SearchTestCase, self).setUp()

        self.query = "rpi"

    def _get_response(self):
        request = "/search/ons?q=" + urllib.quote_plus(self.query)
        response = self.client.get(request)
        return response

    def test_search_status(self):
        response = self._get_response()

        self.assertFalse(response is None)
        self.assertEquals(response.status_code, 200)

    def test_search_response(self):
        response = self._get_response()
        data = response.data

        self.assertFalse(data is False)
        self.assertTrue(isinstance(data, str))

        json_data = json.loads(data)
        self.assertFalse(json_data is None)
        self.assertTrue(isinstance(json_data, dict))

        self.assertTrue("hits" in json_data)
        self.assertTrue("aggs" in json_data)

        self.assertTrue(len(json_data["hits"]) > 0)
        self.assertTrue(len(json_data["aggs"]) > 0)
