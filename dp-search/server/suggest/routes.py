from flask import request, jsonify

from ..app import get_request_param

from . import suggest
from supervised_models import load_supervised_model, SupervisedModels
from suggest_engine import SuggestEngine

from flasgger import swag_from


@suggest.route("/keywords")
@swag_from("swagger/keywords.yml")
def keywords():
    """
    :return:
    """
    query = get_request_param("q")

    # Get predicted keywords
    top_n = int(request.args.get("count", "5"))
    supervised_model = load_supervised_model(SupervisedModels.ONS)
    keywords = supervised_model.keywords(query, top_n=top_n)

    response = {"keywords": keywords}
    return jsonify(response)


@suggest.route("/autocomplete")
@swag_from("swagger/autocomplete.yml")
def autocomplete():
    """
    :return:
    """
    query = get_request_param("q")

    # Gather additional suggestions from word2vec models
    suggestions = SuggestEngine.word2vec_suggest(query)

    response = {"suggestions": suggestions}
    return jsonify(response)
