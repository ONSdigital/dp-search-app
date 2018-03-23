from flask import current_app

from base import BaseTest


class BasicsTestCase(BaseTest):
    def setUp(self):
        super(BasicsTestCase, self).setUp()

    def tearDown(self):
        self.app_context.pop()

    def test_app_exists(self):
        self.assertFalse(current_app is None)

    def test_app_is_testing(self):
        self.assertTrue(current_app.config['TESTING'])
