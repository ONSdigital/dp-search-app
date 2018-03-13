from flask import request

from . import search, ons_search_engine, hits_to_json
from ..suggest.models import Models, load_model, DELIMITER


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


@search.route("/ons")
def content_query():
    """
    API for executing a standard ONS query
    """
    # Get query term from request
    search_term = request.args.get("q")

    # Build any must/should/must_not clauses
    kwargs = {
        "must": request.args.get("must", "").split(),
        "should": request.args.get("should", "").split(),
        "must_not": request.args.get("must_not", "").split()
    }

    # Execute the search
    return execute_search(search_term, **kwargs)


@search.route("/ons/similar")
def similar():
    """
    API which allows for searches based on similar terms to the query string, without allowing for exact
    matches.
    """

    # Get query term from request
    search_term = request.args.get("q")

    # Load the model
    model = load_model(Models.ONS_FT)

    # Determine how many similar terms to get
    count = int(request.args.get("count", "10"))

    # Add positive and negative terms, if supplied
    positive = request.args.get("should", "").split()
    negative = request.args.get("must_not", "").split()

    # Add the current search term as a positive hit
    positive.append(search_term)

    # Get similar terms
    similar_terms = model.wv.most_similar_cosmul(positive=positive, negative=negative, topn=count)
    # Remove scores
    similar_terms = [term[0] for term in similar_terms]

    # Split and keep tokens if in vocabulary
    for term in similar_terms:
        if DELIMITER in term:
            tokens = term.split(DELIMITER)
            for token in tokens:
                if token in model.wv.vocab:
                    similar_terms.append(token)

    # Compute and add the least similar term to the must_not clause
    least_similar = model.wv.doesnt_match(similar_terms)
    similar_terms.remove(least_similar)
    negative.append(least_similar)

    # Remove delimiters and create kwargs
    kwargs = {
        "should": [term.replace(DELIMITER, " ") for term in similar_terms],
        "must_not": [term.replace(DELIMITER, " ") for term in negative]
    }

    # Execute the search
    return execute_search(search_term, **kwargs)
