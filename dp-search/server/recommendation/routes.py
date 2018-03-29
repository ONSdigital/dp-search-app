from flask import jsonify

from . import recommendation
from recommendation_engine import RecommendationEngine

from ..app import get_request_param
from ..suggest.supervised_models import load_supervised_model, SupervisedModels

from flasgger import swag_from


@swag_from("swagger/get_user_recommendations.yml")
@recommendation.route("/user")
def get_user_recommendations():
    model = load_supervised_model(SupervisedModels.ONS)
    engine = RecommendationEngine(model)

    top_n = get_request_param("count", False, default=10)
    recommendations = engine.recommend_labels_for_current_user(top_n)

    response = {"user_keywords": recommendations}
    return jsonify(response)
