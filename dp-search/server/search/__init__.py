from flask import Blueprint, jsonify

from hit import Hit

# Create the search blueprint
search = Blueprint("search", __name__)


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


def _highlight(highlighted_text, val):
    val = val.replace(
        highlighted_text,
        "<strong>%s</strong>" % highlighted_text)

    val = val.replace(
        highlighted_text.lower(),
        "<strong>%s</strong>" % highlighted_text.lower())
    return val


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
                        highlighted_text = " ".join(re.findall(
                            "<strong>(.*?)</strong>", fragment))

                        val = get_var(hit_dict, highlight_key)

                        if hasattr(val, "__iter__"):
                            highlighted_vals = []
                            for v in val:
                                highlighted_vals.append(
                                    _highlight(highlighted_text, v))
                            hit_dict.set_value(highlight_key, highlighted_vals)
                        else:
                            hit_dict.set_value(
                                highlight_key, _highlight(
                                    highlighted_text, val))

        # rename 'type' field to '_type'
        hit_dict["_type"] = hit_dict.pop("type")
        hits_list.append(hit_dict)
    return hits_list


def hits_to_json(
        content_response,
        aggregations,
        paginator,
        sort_by,
        featured_result_response=None):
    """
    Replicates the JSON response of Babbage
    :param content_response:
    :param aggregations:
    :param paginator:
    :param sort_by:
    :param featured_result_response:
    :return:
    """

    featured_result_hits = []
    if featured_result_response is not None:
        featured_result_hits = [h.to_dict()
                                for h in featured_result_response.hits]

    response = {
        "result": {
            "numberOfResults": content_response.hits.total,
            "took": content_response.took,
            "results": marshall_hits(content_response.hits),
            "docCounts": {},
            "paginator": paginator,
            "sortBy": sort_by

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
