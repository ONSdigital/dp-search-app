import enum
import fastText
import numpy as np
from utils import cosine_sim, cosine_sim_matrix

_models = {}


class SupervisedModels(enum.Enum):
    ONS = "ons_supervised.bin"


class SupervisedModel(object):
    def __init__(self, model, supervised_model, prefix="__label__"):
        assert isinstance(model, SupervisedModels)
        assert isinstance(supervised_model, fastText.FastText._FastText)
        self.model = model
        self.supervised_model = supervised_model
        self.prefix = prefix

        # Normalised vectors
        self.input_matrix_normalised = self._normalise_matrix(self.supervised_model.get_input_matrix())
        self.output_matrix_normalised = self._normalise_matrix(self.supervised_model.get_output_matrix())

        # Labels
        self.labels = np.array(self.supervised_model.get_labels())

    @staticmethod
    def _normalise_matrix(matrix):
        norm = np.linalg.norm(matrix, axis=1)
        norm_matrix = np.zeros(matrix.shape)

        for i in range(matrix):
            norm_matrix[i] = matrix[i] / norm[i]
        return norm_matrix

    def get_word_vector(self, word):
        """
        Returns the word vector for this word.
        :param word:
        :return:
        """
        return self.supervised_model.get_word_vector(word)

    def get_label_vector(self, label):
        """
        Returns the word vector for this label.
        :param label:
        :return:
        """
        if label.startswith(self.prefix) is False:
            label = "%s%s" % (self.prefix, label)

        if label in self.labels:
            ix = np.where(self.labels == label)
            vec = self.supervised_model.get_output_matrix()[ix][0]
            return vec
        return np.zeros(self.supervised_model.get_dimension())

    def get_word_for_vector(self, vector):
        """
        Returns the word nearest to the given vector
        :param vector:
        :return:
        """
        cosine_similarity, ix = self._get_index_for_vector(self.input_matrix_normalised, vector)

        word = self.supervised_model.get_words()[ix]
        return word, cosine_similarity[ix]

    def get_label_for_vector(self, vector):
        """
        Returns the label nearest to the given vector
        :param vector:
        :return:
        """
        cosine_similarity, ix = self._get_index_for_vector(self.output_matrix_normalised, vector)

        word = self.labels
        return word, cosine_similarity[ix]

    @staticmethod
    def _get_index_for_vector(matrix, vector):
        cosine_similarity = cosine_sim_matrix(matrix, vector)
        ix = np.abs(cosine_similarity - cosine_similarity.max()).argmin()

        return cosine_similarity, ix

    def keywords(self, text, top_n=10):
        labels, proba = self.supervised_model.predict(text, top_n)

        # Clean up labels
        labels = [label.replace(self.prefix, "") if self.label in label else label for label in labels]

        result = [{"label": label, "P": P} for label, P in zip(labels, proba)]

        # Sort by probability
        result = sorted(result, key=lambda item: item["P"], reverse=True)
        return result

    def similarity(self, word1, word2):
        """
        Computes the similarity between two word vectors by first normalising them
        :param word1:
        :param word2:
        :return:
        """
        vec1 = self.model.get_word_vector(word1)
        vec1 /= np.linalg.norm(vec1)

        vec2 = self.model.get_word_vector(word2)
        vec2 /= np.linalg.norm(vec2)

        return cosine_sim(vec1, vec2)


def init(app):
    import os
    # Get the model dir from the current app config
    model_dir = app.config["SUPERVISED_VECTOR_MODELS_DIR"]
    label = app.config.get("SUPERVISED_VECTOR_LABEL", "__label__")
    for model in SupervisedModels:
        fname = "%s/%s" % (model_dir, model.value)
        if os.path.isfile(fname):
            sm = fastText.load_model(fname)
            _models[model] = SupervisedModel(model, sm, label=label)


def load_supervised_model(model):
    assert isinstance(model, SupervisedModels)
    return _models[model]
