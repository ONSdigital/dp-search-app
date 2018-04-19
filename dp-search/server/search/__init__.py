import os

from flask import Blueprint, jsonify

import fields
from .search_engine import get_search_engine
from hit import Hit

# Create the search blueprint
search = Blueprint("search", __name__)

# Define some utility functions for search

_INDEX = os.environ.get('SEARCH_INDEX', 'ons*')


def ons_search_engine():
    return get_search_engine(_INDEX)


def aggs_to_json(aggregations, key):
    total = 0
    if key in aggregations:
        aggs = aggregations.__dict__["_d_"][key]
        buckets = aggs["buckets"]

        result = {}
        for item in buckets:
            key = item["key"]
            count = item["doc_count"]
            result[key] = count
            total += count

        return result, total
    return {}, total


def get_var(input_dict, accessor_string):
    """Gets data from a dictionary using a dotted accessor-string"""
    current_data = input_dict
    for chunk in accessor_string.split('.'):
        current_data = current_data.get(chunk, {})
    return current_data


def marshall_hits(hits):
    """
    Substitues highlights into fields and returns valid JSON
    :param hits:
    :return:
    """
    import re

    hits_list = []
    for hit in hits:
        hit_dict = Hit(hit.to_dict())
        if hasattr(hit.meta, "highlight"):
            highlight_dict = hit.meta.highlight.to_dict()
            for highlight_key in highlight_dict:
                for fragment in highlight_dict[highlight_key]:
                    fragment = fragment.strip()
                    if "<strong>" in fragment and "</strong>" in fragment:
                        highlighted_text = " ".join(re.findall("<strong>(.*?)</strong>", fragment))

                        val = get_var(hit_dict, highlight_key)

                        val = val.replace(
                            highlighted_text,
                            "<strong>%s</strong>" % highlighted_text)

                        val = val.replace(
                            highlighted_text.lower(),
                            "<strong>%s</strong>" % highlighted_text.lower())

                        hit_dict.set_value(highlight_key, val)

        hit_dict["_type"] = hit_dict.pop("type")  # rename 'type' field to '_type'
        hits_list.append(hit_dict)
    return hits_list


def hits_to_json(content_response, aggregations, paginator, featured_result_response=None):
    """
    Replicates the JSON response of Babbage
    :param content_response:
    :param type_counts_response:
    :param featured_result_response:
    :param page_number:
    :return:
    """

    featured_result_hits = []
    if featured_result_response is not None:
        featured_result_hits = [h.to_dict() for h in featured_result_response.hits]

    response = {
        "result": {
            "numberOfResults": content_response.hits.total,
            "took": content_response.took,
            "results": marshall_hits(content_response.hits),
            "suggestions": [],
            "docCounts": {},
            "paginator": paginator

        },
        "counts": {
            "numberOfResults": content_response.hits.total,
            "docCounts": aggregations
        },
        "featuredResult": {
            "numberOfResults": len(featured_result_hits),
            "results": featured_result_hits
        },
    }

    return jsonify(response)


# Import the routes (this should be done last here)
from routes import *