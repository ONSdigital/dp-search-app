import enum
import fastText

_models = {}


class SupervisedModels(enum.Enum):
    ONS = "ons_supervised_quantized.bin"


class SupervisedModel(object):
    def __init__(self, model, supervised_model, label="__label__"):
        assert isinstance(model, SupervisedModels)
        assert isinstance(supervised_model, fastText.FastText._FastText)
        self.model = model
        self.supervised_model = supervised_model
        self.label = label

    def keywords(self, text, top_n=10):
        labels, proba = self.supervised_model.predict(text, top_n)

        # Clean up labels
        labels = [label.replace(self.label, "") if self.label in label else label for label in labels]

        result = [(label, P) for label, P in zip(labels, proba)]
        return result


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
