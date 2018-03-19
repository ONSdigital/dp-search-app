import os


def _get_jar_fname(path):
    fname = "%s/stanford-ner.jar" % path
    assert (os.path.isfile(fname))

    return fname


def _get_classifier(path):
    fname = "%s/edu/stanford/nlp/models/ner/english.muc.7class.caseless.distsim.crf.ser.gz" % path
    assert (os.path.isfile(fname))

    return fname


def load_stanford_nlp_model():
    from nltk.tag import StanfordNERTagger

    STANFORD_PATH = os.environ.get("STANFORD_NLP_PATH", "../../../stanford-nlp/stanford-ner-2018-02-27/")

    jar_fname = _get_jar_fname(STANFORD_PATH)
    classifier_fname = _get_classifier(STANFORD_PATH)

    return StanfordNERTagger(jar_fname, classifier_fname, "utf-8")
