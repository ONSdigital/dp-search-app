import gensim, enum

DELIMITER = "_"

_models = {}


class Models(enum.Enum):
    ONS_FT = "ons_ft.vec"


def init(app):
    from spelling import init as init_spelling_models
    # Get the model dir from the current app config
    model_dir = app.config["VECTOR_MODELS_DIR"]
    for model in Models:
        fname = "%s/%s" % (model_dir, model.value)
        _models[model] = gensim.models.KeyedVectors.load_word2vec_format(fname, binary=fname.endswith(".bin"))

    # Safe to init spelling models
    init_spelling_models()


def load_model(model):
    assert isinstance(model, Models)
    return _models[model]
