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
        if do_must_must_not:
            params = {"must": self.query, "must_not": self.must_not}

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

    @staticmethod
    def extract_doc_counts(data):
        """
        Extracts total document counts from response aggregation
        :param data:
        :return:
        """
        aggs = data["aggs"]
        buckets = aggs["docCounts"]["buckets"]

        total_counts = 0
        for bucket in buckets:
            total_counts = total_counts + int(bucket["doc_count"])
        return total_counts

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

        self.assertTrue("hits" in json_data)
        self.assertTrue("aggs" in json_data)

        self.assertTrue(len(json_data["hits"]) > 0)
        self.assertTrue(len(json_data["aggs"]) > 0)

    def test_search_must_must_not(self):
        """
        Tests that including a must_not clause leads to less results than a standard query
        :return:
        """
        must_must_not_response = self._get_response(do_must_must_not=True)
        base_response = self._get_response(do_must_must_not=False)

        must_must_not_data = must_must_not_response.data
        json_must_must_not_data = json.loads(must_must_not_data)

        base_data = base_response.data
        json_base_data = json.loads(base_data)

        must_must_not_counts = self.extract_doc_counts(json_must_must_not_data)
        base_counts = self.extract_doc_counts(json_base_data)

        self.assertTrue(must_must_not_counts > 0)
        self.assertTrue(base_counts > 0)

        self.assertTrue(base_counts > must_must_not_counts)
