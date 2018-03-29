from flask import current_app as app
import numpy as np

from ..suggest.supervised_models import load_supervised_model, SupervisedModels

db = app.db
model = load_supervised_model(SupervisedModels.ONS)


def create_user(user_id):
    dim = model.f.get_dimension()
    return User(user_id=user_id, user_vector=np.zeros(dim))


def user_exists(user_id):
    return len(User.objects(user_id=user_id)) > 0


def find_user(user_id):
    return User.objects.get(user_id=user_id)


def delete_user(user_id):
    return find_user(user_id).objects.delete()


def get_current_user():
    from flask import request
    if "_ga" in request.cookies:
        user_id = request.cookies.get("_ga")
        if user_exists(user_id):
            return find_user(user_id)
        else:
            # Create a user
            user = create_user(user_id)
            user.save()
            return user
    return None


class User(db.Document):
    """
    Class to represent a unique user of search, by their GA cookie IDs
    """
    meta = {'collection': 'users'}
    user_id = db.StringField(required=True)
    user_vector = db.ListField(required=True)

    def update_user_vector(self, search_term):
        user_vec = np.array(self.user_vector)
        term_vector = model.get_sentence_vector(search_term)

        # Update the user vector
        if np.all(user_vec == 0):
            self.user_vector = term_vector.tolist()
        else:
            # Move the user vector towards the term vector
            dist = term_vector - np.array(self.user_vector)
            user_vec += dist/4.
            self.user_vector = user_vec.tolist()
        self.save()


