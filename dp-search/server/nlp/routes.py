from flask import request, jsonify

from . import nlp
from ner import get_stanford_ner_client

from flasgger import swag_from


@swag_from("swagger/ner.yml")
@nlp.route("/ner")
def ner():
    query = request.args.get("q", True)
    if query is not None:
        tagger = get_stanford_ner_client()
        entities = tagger.get_entities(query)

        # Populate response
        response = []
        for entity in entities:
            token, tag = entity
            response.append({"token": token, "tag": tag})
        return jsonify(response)

    raise ValueError("Must supply query parameter for route /ner")
