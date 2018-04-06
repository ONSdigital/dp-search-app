from flask import request, render_template
from flask import current_app as app

from . import search, ons_search_engine, hits_to_json
from ..app import get_request_param

from flasgger import swag_from


def execute_search(search_term, **kwargs):
    """
    Simple search API to query Elasticsearch
    """
    from ..users.user_utils import UserUtils, SessionUtils

    # Update user, but don't let it impact search
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
    s = ons_search_engine()

    # Perform thr query
    response = s.type_counts_content_query(search_term, **kwargs).execute()

    # Return the hits as JSON
    return hits_to_json(response)


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

    # Build any must/should/must_not clauses
    kwargs = {
        "must": request.form.get("must", "").split(),
        "should": request.form.get("should", "").split(),
        "must_not": request.form.get("must_not", "").split()
    }

    # Execute the search
    return execute_search(search_term, **kwargs)
