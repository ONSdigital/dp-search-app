from flask import jsonify

from . import recommendation
from recommendation_engine import RecommendationEngine

from ..app import get_request_param, BadRequest
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
    from flask import request

    user_id = request.form.get("user_id", "").strip()
    return get_user_recommendations(user_id)
