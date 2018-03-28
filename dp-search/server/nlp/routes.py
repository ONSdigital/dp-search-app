from flasgger import swag_from
from flask import jsonify

from ner import get_stanford_ner_client
from . import nlp
from ..app import get_request_param


@swag_from("swagger/ner.yml")
@nlp.route("/ner")
def ner():
    query = get_request_param("q", True)
    tagger = get_stanford_ner_client()
    entities = tagger.get_entities(query)

    # Populate response
    response = []
    for entity in entities:
        token, tag = entity
        response.append({"token": token, "tag": tag})
    return jsonify(response)
