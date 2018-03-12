from flask import request
from . import search
from . import ons_search_engine, hits_to_json


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
