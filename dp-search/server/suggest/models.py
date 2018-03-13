import gensim, enum

_models = {}


class Models(enum.Enum):
    ONS_FT = "ons_ft.vec"


def init(app):
    # Get the model dir from the current app config
    model_dir = app.config["VECTOR_MODELS_DIR"]
    for model in Models:
        fname = "%s/%s" % (model_dir, model.value)
        _models[model] = gensim.models.KeyedVectors.load_word2vec_format(fname, binary=fname.endswith(".bin"))


def load_model(model):
    if not isinstance(model, Models):
        raise ValueError("Must be instance of Models enum")
    return _models[model]
