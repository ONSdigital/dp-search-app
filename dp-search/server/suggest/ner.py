import os
from sner import Ner


def get_stanford_ner_client():
    STANFORD_NER_URL = os.environ.get("STANFORD_NER_URL", "localhost")
    STANFORD_NER_PORT = int(os.environ.get("STANFORD_NER_PORT", 9199))
    return Ner(host=STANFORD_NER_URL, port=STANFORD_NER_PORT)
