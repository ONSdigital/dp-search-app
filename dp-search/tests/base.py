import unittest
import abc

# Nosetests will take care of sys.path for this import
from server.app import create_app

app = create_app()


class BaseTest(unittest.TestCase):
    __metaclass__ = abc.ABCMeta  # Abstract class

    def setUp(self):
        self.app = app
        self.app_context = self.app.app_context()
        self.app_context.push()
        self.client = self.app.test_client()
