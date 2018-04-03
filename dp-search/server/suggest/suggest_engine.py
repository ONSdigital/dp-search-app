import collections

from word2vec_models import WordVectorModels


class Suggestion(object):
    def __init__(self, suggestion, confidence):
        self._data = {"suggestion": suggestion, "confidence": confidence}

    def __getitem__(self, item):
        return self._data[item]

    def __str__(self):
        return str(self._data)

    def to_dict(self):
        return self._data

    @property
    def suggestion(self):
        return self["suggestion"]

    @property
    def confidence(self):
        return self["confidence"]


class Suggestions(object):
    """
    Class to hold/sort suggestions and their scores
    """

    def __init__(self, original):
        self.original = original
        self._suggestions = []

    def __iter__(self):
        for item in self._suggestions:
            yield item

    def __contains__(self, item):
        assert isinstance(item, Suggestion), "item must be an instance of 'Suggestion'"
        for suggestion in self:
            if suggestion.suggestion == item.suggestion:
                return True
        return False

    def to_dict(self):
        return self.__json__()

    def __json__(self):
        return {
            "original": self.original,
            "suggestions": [s.to_dict() for s in self.suggestions]
        }

    def append(self, item):
        assert isinstance(item, Suggestion), "item must be an instance of 'Suggestion'"
        self._suggestions.append(item)
        return self

    def extend(self, items):
        assert len(items) > 0, "Must supply non-empty list"
        assert isinstance(items[0], Suggestion), "item must be an instance of 'Suggestion'"
        self._suggestions.extend(items)
        return self

    @property
    def suggestions(self):
        return sorted(self._suggestions, key=lambda item: item.confidence, reverse=True)


class SuggestEngine(object):
    @staticmethod
    def elastic_search_suggest(text):
        """
        Method to get phrase suggestions from Elasticsearch.
        :param text:
        :return:
        """
        from ..search import ons_search_engine, fields

        tokens = text.split()

        s = ons_search_engine()
        for i, token in enumerate(tokens):
            name = "suggest_%d" % i
            s = s.suggest(name, token, phrase={"field": fields.suggestion_field.name})
        result = s.execute_suggest()

        # Build list of suggestions
        suggestions = {}
        for i, token in enumerate(tokens):
            suggest_result = result["suggest_%d" % i]
            if len(suggest_result) > 0:
                for item in suggest_result:
                    options = item["options"]

                    if len(options) > 0:
                        if token not in suggestions:
                            suggestions[token] = Suggestions(token)
                        for option in options:
                            text = option["text"]
                            prob = option["score"]
                            suggestions[token].append(Suggestion(text, prob))

        # Return dict ordered by input tokens
        return _sort_dict_by_tokens(suggestions, tokens)

    @staticmethod
    def word2vec_suggest(text, vector_models=WordVectorModels):
        """
        Returns the most probable corrections for a series of models.
        :param text:
        :param vector_models:
        :return:
        """
        from spell_checker import load_spelling_model

        tokens = text.split()

        suggestions = {}
        for model in vector_models:
            sc = load_spelling_model(model)
            result = sc.correct_terms(tokens)
            for key in result:
                c = result[key]
                suggestion = Suggestion(c["correction"], c["P"])
                if key not in suggestions:
                    suggestions[key] = Suggestions(key)
                if suggestion not in suggestions[key]:
                    suggestions[key].append(suggestion)

        # Return dict ordered by input tokens
        return _sort_dict_by_tokens(suggestions, tokens)

    @staticmethod
    def word2vec_similar(text, vector_models=WordVectorModels, topn=10):
        """
        Returns similar terms for each token in 'text'
        :param text:
        :param vector_models:
        :return:
        """
        from word2vec_models import load_model
        tokens = text.split()

        class SimilarWord(object):
            def __init__(self, word, score, model):
                self.word = word
                self.score = score
                self.model = model

            def __hash__(self):
                return hash(self.word)

            def __repr__(self):
                return str(self.to_dict())

            def __eq__(self, other):
                return isinstance(other, SimilarWord) and other.word == self.word

            def to_dict(self):
                return self.__json__()

            def __json__(self):
                return {
                    "word": self.word,
                    "score": self.score,
                    "model": self.model.name
                }

        similar = {}
        for model in vector_models:
            vec_model = load_model(model)

            for token in tokens:
                similar_to_token = vec_model.similar_by_word(token, topn=topn * 2)
                if len(similar_to_token) > 0:
                    if token not in similar:
                        similar[token] = set()
                    for word, score in similar_to_token:
                        similar_word = SimilarWord(word, score, model)
                        if similar_word not in similar[token]:
                            similar[token].add(similar_word)

        # Sort by scores across models and only keep topn
        for token in similar:
            sorted_list = sorted(similar[token], key=lambda x: x.score, reverse=True)
            similar[token] = sorted_list[:topn]

        return similar


def _sort_dict_by_tokens(input_dict, tokens):
    sorted_dict = collections.OrderedDict()
    for token in tokens:
        sorted_dict[token] = input_dict[token]

    return sorted_dict
