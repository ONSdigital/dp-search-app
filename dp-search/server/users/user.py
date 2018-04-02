from ..suggest.supervised_models import load_supervised_model, SupervisedModels

from flask import current_app as app
import numpy as np

db = app.db

model = load_supervised_model(SupervisedModels.ONS)


class User(db.Document):
    """
    Class to represent a unique user of search, by their GA cookie IDs
    """
    meta = {'collection': 'users'}
    user_id = db.StringField(required=True)
    user_vector = db.ListField(required=True)

    @property
    def user_array(self):
        return np.array(self.user_vector)

    def update_user_vector(self, search_term):
        user_vec = self.user_array
        term_vector = model.get_sentence_vector(search_term)

        # Update the user vector
        if np.all(user_vec == 0):
            self.user_vector = term_vector.tolist()
        else:
            # Move the user vector towards the term vector
            dist = term_vector - user_vec
            user_vec += dist / 4.
            self.user_vector = user_vec.tolist()
        self.save()


class Session(db.Document):
    """
    Class to represent a single user session
    """
    meta = {'collection': 'user_sessions'}
    user_id = db.ObjectIdField(required=True)
    session_id = db.StringField(required=True)

    def time_created(self):
        return self.id.generation_time
