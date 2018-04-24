from ..suggest.supervised_models import load_supervised_model, SupervisedModels

from flask import current_app as app
import numpy as np

db = app.db

model = load_supervised_model(SupervisedModels.ONS)


def default_distance_measure(original_vector, term_vector):
    assert isinstance(
        original_vector, np.ndarray), "original vector must be instance of np.ndarray"
    assert isinstance(
        term_vector, np.ndarray), "term vector must be instance of np.ndarray"

    dist = term_vector - original_vector
    return dist


def default_move_session_vector(original_vector, term_vector):
    """
    Default method to modify a session vector to reflect interest in a term vector.
    :param original_vector: Word vector representing the present session.
    :param term_vector: Word vector representing the term of interest.
    :return: An updated word vector which has moved towards the term vector in the full N-dimensional
    vector space.
    """
    dist = default_distance_measure(original_vector, term_vector)

    return original_vector + dist / 4


class User(db.Document):
    """
    Class to represent a unique user of search, by their GA cookie IDs
    """
    meta = {'collection': 'users'}
    user_id = db.StringField(required=True)

    def get_user_vector(self):
        """
        Get recent sessions and compute the User vector
        :return:
        """
        from user_utils import SessionUtils
        # Sort sessions in descending order and limit to 10 items
        sessions = SessionUtils.get_sessions_for_user(
            self).order_by("-id").limit(10)

        if len(sessions) > 0:
            # Compute vector weights which decay exponentially over time
            count = len(sessions)
            # Last weight is normalised to 1.0
            weights = np.array([np.exp(c)
                                for c in range(count)]) / np.exp(count - 1)

            # Reverse the weights to match session ordering
            weights = weights[::-1]

            # Combine vectors and weights
            vectors = np.array(
                [s.session_array * w for s, w in zip(sessions, weights)])

            # Average
            user_vec = np.mean(vectors, axis=0)

            return user_vec
        return None


class Session(db.Document):
    """
    Class to represent a single user session
    """
    meta = {'collection': 'user_sessions'}
    user_id = db.ObjectIdField(required=True)
    session_id = db.StringField(required=True)

    # Learning
    session_vector = db.ListField(required=True)

    def time_created(self):
        return self.id.generation_time

    @property
    def session_array(self):
        return np.array(self.session_vector)

    def update_session_vector(
            self,
            search_term,
            update_func=default_move_session_vector,
            **kwargs):
        """

        :param search_term:
        :param update_func: Callable - function which takes the original session vector, term vector
        and (optional) kwargs and updates the session vector to reflect user interest.
        :return:
        """
        session_vec = self.session_array
        term_vector = model.get_sentence_vector(search_term)

        # Update the user vector
        if np.all(session_vec == 0):
            self.session_vector = term_vector.tolist()
        else:
            # Move the user vector towards the term vector
            new_session_vec = update_func(session_vec, term_vector, **kwargs)
            self.session_vector = new_session_vec.tolist()
        self.save()
