from flask import current_app as app

db = app.db


def create_user(user_id):
    return User(user_id=user_id)


def save_user(user):
    return user.save()


def user_exists(user_id):
    return len(User.objects(user_id=user_id)) > 0


def find_user(user_id):
    return User.objects.get(user_id=user_id)


def delete_user(user_id):
    return find_user(user_id).objects.delete()


class User(db.Document):
    """
    Class to represent a unique user of search, by their GA cookie IDs
    """
    meta = {'collection': 'users'}
    user_id = db.StringField(required=True)
