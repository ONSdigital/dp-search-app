from word2vec_models import WordVectorModels, load_model
from gensim.models.keyedvectors import EuclideanKeyedVectors


class SpellChecker(object):
    def __init__(self, word2vec):
        assert isinstance(word2vec, EuclideanKeyedVectors)

        # Collect ranked list of words in vocab
        words = word2vec.index2word

        w_rank = {}
        for i, word in enumerate(words):
            w_rank[word] = i
        self.words = w_rank

    def correct_terms(self, terms):
        result = {}
        for term in terms:
            result[term] = self.correction(term)
        return result

    def P(self, word):
        """ Probability of `word`. """
        # use inverse of rank as proxy
        # returns 0 if the word isn't in the dictionary
        return - self.words.get(word, 0)

    def correction(self, word):
        """ Most probable spelling correction for word. """
        return max(self.candidates(word), key=self.P)

    def candidates(self, word):
        """ Generate possible spelling corrections for word. """
        return self.known([word]) or self.known(self.edits1(word)) or self.known(self.edits2(word)) or [word]

    def known(self, words):
        """ The subset of `words` that appear in the dictionary of WORDS. """
        return set(w for w in words if w in self.words)

    def edits1(self, word):
        """ All edits that are one edit away from `word`. """
        letters = 'abcdefghijklmnopqrstuvwxyz'
        splits = [(word[:i], word[i:]) for i in range(len(word) + 1)]
        deletes = [L + R[1:] for L, R in splits if R]
        transposes = [L + R[1] + R[0] + R[2:] for L, R in splits if len(R) > 1]
        replaces = [L + c + R[1:] for L, R in splits if R for c in letters]
        inserts = [L + c + R for L, R in splits for c in letters]
        return set(deletes + transposes + replaces + inserts)

    def edits2(self, word):
        """ All edits that are two edits away from `word`. """
        return (e2 for e1 in self.edits1(word) for e2 in self.edits1(e1))


_models = {}


def init():
    for model in WordVectorModels:
        _models[model] = SpellChecker(load_model(model))


def load_spelling_model(model):
    if not isinstance(model, WordVectorModels):
        raise ValueError("Must be instance of Models enum")
    return _models[model]
