from . import suggest
from models import Models, load_model
from spelling import load_spelling_model
from flask import jsonify, request


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


@suggest.route("/spelling")
def spelling():
    model = load_spelling_model(Models.ONS_FT)

    query = request.args.get("q")
    if query is not None:
        terms = query.split()

        result = model.correct_terms(terms)
        return jsonify(result)
    raise ValueError("Must supply query parameter for route /similar")
