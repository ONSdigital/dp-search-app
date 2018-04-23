from flask import current_app as app

from ..suggest.supervised_models import SupervisedModel


class RecommendationEngine(object):
    """
    Class to serve user recommendations
    TODO - Track User session vectors and predict future trends (using neural nets?)
    """

    def __init__(self, model):
        assert isinstance(model, SupervisedModel)
        self.model = model

    def recommend_labels_for_user(self, user, top_n=10):
        """
        Calculates ONS keyword labels for the current user
        :param user:
        :param top_n:
        :return:
        """
        from ..users.user import User

        assert isinstance(user, User), "Must supply instance of user"
        user_vector = user.get_user_vector()
        if user_vector is not None and len(user_vector) > 0:
            top_labels, similarity = self.model.get_labels_for_vector(
                user_vector, top_n)
            result = sorted([{"keyword": k, "similarity": s} for k, s in zip(
                top_labels, similarity)], key=lambda x: x["similarity"], reverse=True)

            return result
        return []
