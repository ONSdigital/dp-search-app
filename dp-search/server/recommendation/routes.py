from flask import jsonify

from . import recommendation
from recommendation_engine import RecommendationEngine

from ..app import get_request_param, BadRequest
from ..suggest.supervised_models import load_supervised_model, SupervisedModels

from flasgger import swag_from


@swag_from("swagger/get_user_recommendations.yml")
@recommendation.route("/user")
def get_user_recommendations():
    from ..users.user_utils import UserUtils

    user = UserUtils.get_current_user()
    if user:
        model = load_supervised_model(SupervisedModels.ONS)
        engine = RecommendationEngine(model)

        top_n = int(get_request_param("count", False, default=10))
        recommendations = engine.recommend_labels_for_user(user, top_n)

        response = {"user_keywords": recommendations}
        return jsonify(response)

    raise BadRequest("User does not exist")
