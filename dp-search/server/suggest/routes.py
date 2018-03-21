from flask import request, jsonify

from . import suggest
from suggest_engine import SuggestEngine


@suggest.route("/autocomplete")
def autocomplete():
    query = str(request.args.get("q"))
    if query is not None:
        # Gather additional suggestions from word2vec models
        suggestions = SuggestEngine.most_probable_corrections(query)

        # Get predicted keywords
        top_n = int(request.args.get("count", "5"))
        keywords = SuggestEngine.keywords(query, top_n=top_n)

        response = {"suggestions": suggestions, "keywords": keywords}
        return jsonify(response)

    raise ValueError("Must supply query parameter for route /autocomplete")
