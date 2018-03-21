from ner import get_stanford_ner_client


class RecommendationEngine(object):
    def __init__(self):
        self.tagger = get_stanford_ner_client()
