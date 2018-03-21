from flask import Blueprint, jsonify
from .search_engine import get_search_engine
import os

# Create the search blueprint
search = Blueprint("search", __name__)

# Define some utility functions for search

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


# Import the routes (this should be done last here)
from . import routes
