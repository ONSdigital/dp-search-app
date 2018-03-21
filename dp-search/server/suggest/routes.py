from flask import jsonify, request

from ner import get_stanford_ner_client
from spelling import most_probable_corrections
from supervised_models import SupervisedModels, load_supervised_model
from word2vec_models import WordVectorModels, load_model
from . import suggest
from ..search import ons_search_engine, fields


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


def elastic_search_suggest(terms):
    # Create Elasticsearch client for suggestions
    s = ons_search_engine()
    # Create the suggest query
    for field in fields.suggestion_fields:
        for term in terms:
            s = s.suggest("search_suggest", term, phrase={"field": field.name})
    # Execute the query
    suggest_response = s.execute()
    if hasattr(suggest_response, "suggest"):
        suggest_response = suggest_response.suggest.to_dict()["search_suggest"]
    else:
        suggest_response = None
    return suggest_response


@suggest.route("/autocomplete")
def autocomplete():
    tagger = get_stanford_ner_client()
    supervised_model = load_supervised_model(SupervisedModels.ONS)

    query = request.args.get("q")
    if query is not None:
        # Split on whitespace
        terms = query.split()

        # Gather additional suggestions from word2vec models
        result = most_probable_corrections(WordVectorModels, terms)

        tags = tagger.get_entities(" ".join([result[key]["text"] for key in terms]))

        suggestions = [{"text": name, "tag": tag} for name, tag in tags]

        # Get predicted keywords
        top_n = int(request.args.get("count", "5"))
        keywords = supervised_model.keywords(query, top_n=top_n)

        response = {"suggestions": suggestions, "keywords": keywords}
        return jsonify(response)

    raise ValueError("Must supply query parameter for route /autocomplete")
