from flasgger import swag_from
from flask import jsonify

from ..requests import get_request_param

from . import suggest
from suggest_engine import SuggestEngine
from ..word_embedding.supervised_models import load_supervised_model, SupervisedModels


@suggest.route("/keywords")
@swag_from("swagger/keywords.yml")
def keywords():
    """
    :return:
    """
    from ..utils import is_number

    query = get_request_param("q", True)

    # Get predicted keywords
    top_n = get_request_param("top_n", False, default=5)
    if is_number(top_n):
        top_n = int(top_n)
    else:
        from ..exceptions.requests import BadRequest
        raise BadRequest(
            "count specified but is not a number in route '/suggest/keywords'")

    supervised_model = load_supervised_model(SupervisedModels.ONS)
    kws = supervised_model.keywords(query, top_n=top_n)

    response = {"keywords": kws}
    return jsonify(response)


@suggest.route("/autocomplete")
@swag_from("swagger/autocomplete.yml")
def autocomplete():
    """
    :return:
    """
    query = get_request_param("q", True)

    # Gather additional suggestions from word2vec models
    suggestions = SuggestEngine.word2vec_suggest(query)

    response = {"suggestions": suggestions}
    return jsonify(response)
