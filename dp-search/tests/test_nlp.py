import urllib

from base import BaseTest

from flask import json

LOCATION = "LOCATION"
ORGANIZATION = "ORGANIZATION"
MISC = "O"


class NLPTestCase(BaseTest):
    def setUp(self):
        super(NLPTestCase, self).setUp()

        self.query = "London based NHS hospitals"
        self.expected = {
            "London": LOCATION,
            "NHS": ORGANIZATION,
            "based": MISC,
            "hospitals": MISC
        }

    def test_ner_status(self):
        request = "/nlp/ner?q=" + urllib.quote_plus(self.query)
        response = self.client.get(request)

        self.assertFalse(response is None)
        self.assertEqual(response.status_code, 200)

    def test_ner_tags(self):
        request = "/nlp/ner?q=" + urllib.quote_plus(self.query)
        response = self.client.get(request)

        data = response.data

        self.assertFalse(data is None)
        self.assertTrue(isinstance(data, str))

        json_data = json.loads(data)
        self.assertFalse(json_data is None)
        self.assertTrue(isinstance(json_data, list))
        self.assertTrue(len(json_data) > 0)

        for item in json_data:
            self.assertTrue("token" in item)
            self.assertTrue("tag" in item)

            self.assertTrue(item["token"] in self.expected)
            token = item["token"]
            self.assertEquals(item["tag"], self.expected[token])
