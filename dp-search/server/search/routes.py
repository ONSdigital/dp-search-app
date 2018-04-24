from flask import render_template
from flask import current_app as app

from . import search, hits_to_json, aggs_to_json
from search_engine import get_client, get_index, SearchEngine
from paginator import Paginator, MAX_VISIBLE_PAGINATOR_LINK
from sort_by import SortFields

from ..app import get_request_param, get_form_param

from flasgger import swag_from


def execute_search(search_term, sort_by, **kwargs):
    """
    Simple search API to query Elasticsearch
    """
    # Get the Elasticsearch client
    client = get_client()

    # Perform the search
    ons_index = get_index()

    # Init SearchEngine
    s = SearchEngine(using=client, index=ons_index)

    # Define type counts (aggregations) query
    s = s.type_counts_query(search_term)

    # Execute
    type_counts_response = s.execute()

    # Format the output
    aggregations, total_hits = aggs_to_json(
        type_counts_response.aggregations, "docCounts")

    # Setup paginator
    page_number = int(get_form_param("page", False, 1))
    page_size = int(get_form_param("size", False, 10))

    paginator = None

    if total_hits > 0:
        paginator = Paginator(
            total_hits,
            MAX_VISIBLE_PAGINATOR_LINK,
            page_number,
            page_size)

    # Perform the content query to populate the SERP

    # Init SearchEngine
    s = SearchEngine(using=client, index=ons_index)

    # Define the query with sort and paginator
    s = s.content_query(
        search_term, sort_by=sort_by, paginator=paginator, **kwargs)

    # Execute the query
    content_response = s.execute()

    # Check for featured results
    featured_result_response = None
    # Only do this if we have results and are on the first page
    if total_hits > 0 and paginator.current_page <= 1:
        # Init the SearchEngine
        s = SearchEngine(using=client, index=ons_index)

        # Define the query
        s = s.featured_result_query(search_term)

        # Execute the query
        featured_result_response = s.execute()

        # Update user, but catch any exceptions to prevent errors with search
        if app.config["SEARCH_ONLY"] is False:
            from ..users.user_utils import UserUtils, SessionUtils

            try:
                user = UserUtils.get_current_user()
                if user is not None:
                    session = SessionUtils.get_current_session(user)
                    if session is not None:
                        with app.app_context():
                            app.logger.info(
                                "Updating session vector: %s:%s" %
                                (user.user_id, session.session_id))
                        session.update_session_vector(search_term)
            except Exception as e:
                with app.app_context():
                    app.logger.error(
                        "Unable to update user '%s:%s'" %
                        (user.id, user.user_id))
                    app.logger.exception(str(e))

    # Return the hits as JSON
    return hits_to_json(
        content_response,
        aggregations,
        paginator,
        sort_by.name,
        featured_result_response=featured_result_response)


@search.route("/")
def index():
    return render_template("search.html")


@swag_from("swagger/content_query.yml")
@search.route("/ons", methods=["POST"])
def content_query():
    """
    API for executing a standard ONS query
    """
    # Get query term from request
    search_term = get_request_param("q", True)

    # Get any content type filters
    type_filters = get_form_param("filter", False, None)

    # Get sort_by. Default to relevance
    sort_by_str = get_form_param("sort_by", False, "relevance")
    sort_by = SortFields[sort_by_str]

    # Execute the search
    response = execute_search(
        search_term,
        sort_by,
        type_filters=type_filters)
    return response
