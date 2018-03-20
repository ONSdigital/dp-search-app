from flask import jsonify, request

from . import suggest
from models import Models, load_model
from spelling import load_spelling_model

# NER server
from sner import Ner

tagger = Ner(host='localhost', port=9199)


@suggest.route("/similar/<word>")
def similar(word):
    model = load_model(Models.ONS_FT)

    count = int(request.args.get("count", "10"))
    similar_words = model.wv.similar_by_word(word, count)
    return jsonify(similar_words)


@suggest.route("/similar")
def similar_by_query():
    model = load_model(Models.ONS_FT)

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
    model = load_spelling_model(Models.ONS_FT)

    query = request.args.get("q")
    if query is not None:
        terms = query.split()
        result = model.correct_terms(terms)

        tags = tagger.get_entities(" ".join([result[key] for key in terms]))

        res = [{"name": name, "tag": tag} for name, tag in tags]

        # TODO - Populate keywords
        # TODO - Incorporate Elasticsearch suggest API
        return jsonify({"result": res, "keywords": []})
    raise ValueError("Must supply query parameter for route /autocomplete")
