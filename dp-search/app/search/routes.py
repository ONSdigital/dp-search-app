from flask import request, jsonify
from . import search

from .engine import get_search_engine
import json

_INDEX = "ons*"


def hits_to_json(search_response):
    hits = {
        "hits": [
            h.to_dict() for h in search_response.hits
        ]
    }
    return jsonify(hits)


@search.route('/')
def index():
    return "Hello, World!"


@search.route('/search')
def search():
    '''
    Simple search API to query Elasticsearch
    '''
    print "Here"

    # Get query term from request
    search_term = request.args.get("q")

    # Perform the search
    s = get_search_engine(_INDEX)

    # Perform thr query
    response = s.type_counts_content_query(search_term).execute()

    # Return the hits as JSON
    return hits_to_json(response)
