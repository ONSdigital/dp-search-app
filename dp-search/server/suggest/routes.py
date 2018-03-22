from flask import request, jsonify

from . import suggest
from supervised_models import load_supervised_model, SupervisedModels
from suggest_engine import SuggestEngine


@suggest.route("/autocomplete")
def autocomplete():
    query = str(request.args.get("q"))
    if query is not None:
        # Gather additional suggestions from word2vec models
        suggestions = SuggestEngine.word2vec_suggest(query)

        # Get predicted keywords
        top_n = int(request.args.get("count", "5"))
        supervised_model = load_supervised_model(SupervisedModels.ONS)
        keywords = supervised_model.keywords(query, top_n=top_n)

        response = {"suggestions": suggestions, "keywords": keywords}
        return jsonify(response)

    raise ValueError("Must supply query parameter for route /autocomplete")
