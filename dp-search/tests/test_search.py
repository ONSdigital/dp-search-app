import urllib

from flask import json

from base import BaseTest


class SearchTestCase(BaseTest):
    def setUp(self):
        super(SearchTestCase, self).setUp()

        self.query = "rpi"
        self.must_not = "cpi"

    def _get_response(self, do_must_must_not=True):
        """
        Executes the test query and returns the response
        :return:
        """
        request = "/search/ons?q=" + urllib.quote_plus(self.query)

        params = {}

        response = self.client.post(request, data=params)
        return response

    def test_search_status(self):
        """
        Executes the test query and ensures a 200 OK response
        :return:
        """
        response = self._get_response()

        self.assertFalse(response is None)
        self.assertEquals(response.status_code, 200)

    def test_search_response(self):
        """
        Makes sure all necessary keys are in response data and have non-zero lengths
        :return:
        """
        response = self._get_response()
        data = response.data

        # Make sure response data exists
        self.assertFalse(data is False)
        self.assertTrue(isinstance(data, str))

        json_data = json.loads(data)
        self.assertFalse(json_data is None)
        self.assertTrue(isinstance(json_data, dict))

        self.assertTrue("result" in json_data)
        self.assertTrue("counts" in json_data)
        self.assertTrue("docCounts" in json_data["counts"])
        self.assertTrue("featuredResult" in json_data)

        hits = json_data["result"]["results"]
        aggs = json_data["counts"]
        featured = json_data["featuredResult"]

        self.assertTrue(len(hits) > 0)
        self.assertTrue(aggs["numberOfResults"] > 0)
        self.assertEqual(featured["numberOfResults"], 1)
