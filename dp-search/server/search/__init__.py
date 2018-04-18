from flask import Blueprint, jsonify
from .search_engine import get_search_engine
import os
import fields

# Create the search blueprint
search = Blueprint("search", __name__)

# Define some utility functions for search

_INDEX = os.environ.get('SEARCH_INDEX', 'ons*')


def ons_search_engine():
    return get_search_engine(_INDEX)


def aggs_to_json(aggregations, key):
    if key in aggregations:
        aggs = aggregations.__dict__["_d_"][key]
        buckets = aggs["buckets"]

        result = {}
        for item in buckets:
            key = item["key"]
            count = item["doc_count"]
            result[key] = count

        return result
    return {}


def marshall_hits(hits):
    """
    Substitues highlights into fields and returns valid JSON
    :param hits:
    :return:
    """
    hits_list = []
    for hit in hits:
        hit_dict = hit.to_dict()
        if hasattr(hit.meta, "highlight") and fields.title.name in hit.meta.highlight:
            for fragment in hit.meta.highlight[fields.title.name]:
                if fragment.startswith("<strong>"):
                    highlighted_text = fragment.replace("<strong>", "").replace("</strong>", "")
                    hit_dict["description"]["title"] = hit_dict["description"]["title"].replace(highlighted_text,
                                                                                                    fragment)
        hits_list.append(hit_dict)
    return hits_list


def hits_to_json(content_response, featured_result_response):
    """
    Replicates the JSON response of Babbage
    :param content_response:
    :param featured_result_response:
    :return:
    """
    num_results = len(content_response.hits)

    aggregations = aggs_to_json(content_response.aggregations, "docCounts")

    response = {
        "result": {
            "numberOfResults": num_results,
            "took": content_response.took,
            "results": marshall_hits(content_response.hits),
            "suggestions": [],
            "docCounts": {}

        },
        "counts": {
            "docCounts": aggregations
        },
        "featuredResult": {
            "results": [h.to_dict() for h in featured_result_response.hits]
        },
    }

    return jsonify(response)


# Import the routes (this should be done last here)
from . import routes
