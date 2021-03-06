from flask import jsonify
from flask import current_app as app

from . import recommendation
from recommendation_engine import RecommendationEngine

from ..requests import get_request_param, get_form_param
from ..word_embedding.supervised_models import load_supervised_model, SupervisedModels
from ..exceptions.requests import BadRequest

from flasgger import swag_from


def get_user_recommendations(user_id, top_n):
    from ..users.user_utils import UserUtils

    if UserUtils.user_exists(user_id):
        user = UserUtils.find_user(user_id)

        model = load_supervised_model(SupervisedModels.ONS)
        engine = RecommendationEngine(model)

        recommendations = engine.recommend_labels_for_user(user, top_n)

        response = {"user_keywords": recommendations}
        return jsonify(response)

    raise BadRequest("User does not exist")


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


@swag_from("swagger/current_user_recommendations.yml")
@recommendation.route("/user")
def current_user_recommendations():
    from ..users.user_utils import UserUtils

    user_id = UserUtils.get_current_user_id()
    top_n = int(get_request_param("top_n", False, default=10))
    return get_user_recommendations(user_id, top_n)


@swag_from("swagger/update_session.yml")
@recommendation.route("/user/update", methods=["POST"])
def update_session():
    """
    Update a user session to show positive/negative interest in a term
    :return:
    """
    from ..users.user_utils import UserUtils, SessionUtils

    term = get_form_param("term", True)
    sentiment = get_form_param("sentiment", True)

    possible_sentiments = ["positive", "negative"]
    if sentiment in possible_sentiments:
        user_id = UserUtils.get_current_user_id()
        if user_id is not None:
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
    top_n = int(get_request_param("top_n", False, default=10))
    return get_user_recommendations(user_id, top_n)
