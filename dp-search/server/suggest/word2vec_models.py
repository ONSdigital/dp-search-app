import enum
import gensim

DELIMITER = "_"

_models = {}


class WordVectorModels(enum.Enum):
    ONS_FT = "ons_ft.vec"
    GOOGLE_SLIM = "GoogleNews-vectors-negative300-SLIM.bin"

    def __str__(self):
        return self.value


def init(app):
    from spell_checker import init as init_spelling_models
    # Get the model dir from the current app config
    model_dir = app.config["VECTOR_MODELS_DIR"]
    for model in WordVectorModels:
        fname = "%s/%s" % (model_dir, model)
        _models[model] = gensim.models.KeyedVectors.load_word2vec_format(
            fname, binary=fname.endswith(".bin"))

    # Safe to init spelling models
    init_spelling_models()


def load_model(model):
    assert isinstance(model, WordVectorModels)
    return _models[model]
