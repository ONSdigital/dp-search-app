from flask import current_app as app

from ..suggest.supervised_models import SupervisedModel


class RecommendationEngine(object):
    """
    Class to serve user recommendations
    """

    def __init__(self, model):
        assert isinstance(model, SupervisedModel)
        self.model = model

    def recommend_labels_for_current_user(self, top_n=10):
        """
        Calculates ONS keyword labels for the current user
        :param top_n:
        :return:
        """
        from ..users.user import get_current_user

        user = get_current_user()
        if user is not None:
            top_labels, similarity = self.model.get_labels_for_vector(user.user_array, top_n)
            result = [{"keyword": k, "similarity": s} for k, s in zip(top_labels, similarity)]
            with app.app_context():
                app.logger.debug("User recommended keywords: %s" % result)
            return result
        return []
