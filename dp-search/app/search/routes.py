from flask import request, jsonify
from . import search

from .engine import get_search_engine
import json
import os

_INDEX = os.environ.get('SEARCH_INDEX', 'ons*')


def ons_search_engine():
    return get_search_engine(_INDEX)


def aggs_to_json(aggs):
    return aggs.__dict__["_d_"]


def hits_to_json(search_response):
    hits = {
        "hits": [
            h.to_dict() for h in search_response.hits
        ]
    }

    if hasattr(search_response, "aggregations"):
        hits["aggs"] = aggs_to_json(search_response.aggregations)

    return jsonify(hits)


@search.route("/ons")
def search():
    '''
    Simple search API to query Elasticsearch
    '''

    # Get query term from request
    search_term = request.args.get("q")

    # Perform the search
    s = ons_search_engine()

    # Perform thr query
    response = s.type_counts_content_query(search_term).execute()

    # Return the hits as JSON
    return hits_to_json(response)
