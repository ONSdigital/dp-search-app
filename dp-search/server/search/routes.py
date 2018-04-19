from flask import render_template
from flask import current_app as app

from . import search, ons_search_engine, hits_to_json, aggs_to_json
from paginator import Paginator, MAX_VISIBLE_PAGINATOR_LINK, RESULTS_PER_PAGE

from ..app import get_request_param, get_form_param

from flasgger import swag_from


def execute_search(search_term, **kwargs):
    """
    Simple search API to query Elasticsearch
    """
    # Update user, but don't let it impact search
    if app.config["SEARCH_ONLY"] is False:
        from ..users.user_utils import UserUtils, SessionUtils

        try:
            user = UserUtils.get_current_user()
            if user is not None:
                session = SessionUtils.get_current_session(user)
                if session is not None:
                    with app.app_context():
                        app.logger.info("Updating session vector: %s:%s" % (user.user_id, session.session_id))
                    session.update_session_vector(search_term)
        except Exception as e:
            with app.app_context():
                app.logger.error("Unable to update user '%s:%s'" % (user.id, user.user_id))
                app.logger.exception(str(e))

    # Perform the search
    """
    TODO - Replace below with MultiSearch
    """

    s = ons_search_engine().type_counts_query(search_term)
    type_counts_response = s.execute()

    aggregations, total_hits = aggs_to_json(type_counts_response.aggregations, "docCounts")

    page_number = int(get_form_param("page", False, 1))
    page_size = int(get_form_param("size", False, 10))

    paginator = Paginator(total_hits, MAX_VISIBLE_PAGINATOR_LINK, page_number, page_size)

    # Perform the query
    s = ons_search_engine().content_query(search_term, paginator, **kwargs)
    content_response = s.execute()

    featured_result_response = None
    if paginator.current_page <= 1:
        s = ons_search_engine().featured_result_query(search_term)
        featured_result_response = s.execute()

    # Return the hits as JSON
    return hits_to_json(content_response, aggregations, paginator, featured_result_response=featured_result_response)


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
    type_filters = get_form_param("filter", False, None)

    # Execute the search
    return execute_search(search_term, type_filters=type_filters)
