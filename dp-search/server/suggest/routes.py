from flask import jsonify, request

from . import suggest
from word2vec_models import WordVectorModels, load_model
from supervised_models import SupervisedModels, load_supervised_model
from spelling import load_spelling_model

# NER server
from sner import Ner

tagger = Ner(host='localhost', port=9199)


@suggest.route("/similar/<word>")
def similar(word):
    model = load_model(WordVectorModels.ONS_FT)

    count = int(request.args.get("count", "10"))
    similar_words = model.wv.similar_by_word(word, count)
    return jsonify(similar_words)


@suggest.route("/similar")
def similar_by_query():
    model = load_model(WordVectorModels.ONS_FT)

    query = request.args.get("q")
    if query is not None:
        terms = query.split()

        negative = request.args.get("n")
        if negative is not None:
            negative = negative.split()

        count = int(request.args.get("count", 10))

        similar_words = model.wv.most_similar_cosmul(positive=terms, negative=negative, topn=count)
        return jsonify(similar_words)
    raise ValueError("Must supply query parameter for route /similar")


@suggest.route("/autocomplete")
def autocomplete():
    sc = load_spelling_model(WordVectorModels.ONS_FT)
    supervised_model = load_supervised_model(SupervisedModels.ONS)

    query = request.args.get("q")
    if query is not None:
        terms = query.split()
        result = sc.correct_terms(terms)

        tags = tagger.get_entities(" ".join([result[key] for key in terms]))

        res = [{"name": name, "tag": tag} for name, tag in tags]

        # Get predicted keywords
        top_n = int(request.args.get("count", "10"))
        keywords = supervised_model.keywords(query, top_n=top_n)

        # TODO - Incorporate Elasticsearch suggest API
        return jsonify({"result": res, "keywords": keywords})
    raise ValueError("Must supply query parameter for route /autocomplete")
