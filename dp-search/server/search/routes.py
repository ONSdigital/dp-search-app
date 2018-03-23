from flask import request, render_template

from . import search, ons_search_engine, hits_to_json
from ..app import get_request_param

from flasgger import swag_from


def execute_search(search_term, **kwargs):
    """
    Simple search API to query Elasticsearch
    """

    # Perform the search
    s = ons_search_engine()

    # Perform thr query
    response = s.type_counts_content_query(search_term, **kwargs).execute()

    # Return the hits as JSON
    return hits_to_json(response)


@search.route("/")
def index():
    return render_template("search.html")


@swag_from("swagger/content_query.yml")
@search.route("/ons")
def content_query():
    """
    API for executing a standard ONS query
    """
    # Get query term from request
    search_term = get_request_param("q", True)

    # Build any must/should/must_not clauses
    kwargs = {
        "must": request.args.get("must", "").split(),
        "should": request.args.get("should", "").split(),
        "must_not": request.args.get("must_not", "").split()
    }

    # Execute the search
    return execute_search(search_term, **kwargs)
