from flask import jsonify
from flask import current_app as app

from . import recommendation
from recommendation_engine import RecommendationEngine

from ..app import get_request_param, get_form_param, BadRequest
from ..suggest.supervised_models import load_supervised_model, SupervisedModels

from flasgger import swag_from


def get_user_recommendations(user_id):
    from ..users.user_utils import UserUtils

    if UserUtils.user_exists(user_id):
        user = UserUtils.find_user(user_id)

        model = load_supervised_model(SupervisedModels.ONS)
        engine = RecommendationEngine(model)

        top_n = int(get_request_param("count", False, default=10))
        recommendations = engine.recommend_labels_for_user(user, top_n)

        response = {"user_keywords": recommendations}
        return jsonify(response)

    raise BadRequest("User does not exist")


@swag_from("swagger/current_user_recommendations.yml")
@recommendation.route("/user")
def current_user_recommendations():
    from ..users.user_utils import UserUtils

    user_id = UserUtils.get_current_user_id()
    return get_user_recommendations(user_id)


@swag_from("swagger/recommendations_by_id.yml")
@recommendation.route("/user/id", methods=["POST"])
def recommendations_by_id():
    user_id = get_form_param("user_id", True)
    return get_user_recommendations(user_id)


def update_session_by_sentiment(
        original_vector,
        term_vector,
        sentiment="positive"):
    from ..users.user import default_distance_measure

    dist = default_distance_measure(original_vector, term_vector)

    if sentiment == "positive":
        return original_vector + dist / 4
    elif sentiment == "negative":
        return original_vector - dist / 4
    else:
        raise Exception("Unknown sentiment: %s" % sentiment)


@swag_from("swagger/update_session.yml")
@recommendation.route("/user/update", methods=["POST"])
def update_session():
    """
    Update a user session to show positive/negative interest in a term
    :return:
    """
    from ..users.user_utils import UserUtils, SessionUtils

    user_id = get_form_param("user_id", True)
    term = get_form_param("term", True)
    sentiment = get_form_param("sentiment", True)

    possible_sentiments = ["positive", "negative"]
    if sentiment in possible_sentiments:
        user = UserUtils.find_user(user_id)
        if user is not None:
            session = SessionUtils.get_current_session(user)
            if session is not None:
                with app.app_context():
                    app.logger.info(
                        "Updating session vector: %s:%s" %
                        (user.user_id, session.session_id))
                session.update_session_vector(
                    term, update_func=update_session_by_sentiment, sentiment=sentiment)

        else:
            raise BadRequest("Unknown user: %s" % user_id)
    else:
        raise BadRequest("Unsupported sentiment: %s" % sentiment)

    # Return the new (updated) recommendations
    return get_user_recommendations(user_id)
