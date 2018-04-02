from numpy import zeros
from user import model, User, Session


def get_current_user():
    user_id = get_current_user_id()
    if user_id:
        if user_exists(user_id):
            return find_user(user_id)
        else:
            # Create a user
            user = create_user(user_id)

            # Create a user session if it doesn't exist
            session_id = get_current_session_id()
            if session_id and session_exits(user, session_id) is False:
                session = create_session(user, session_id)
                session.save()

            # Save the user
            user.save()
            return user
    return None


def create_user(user_id):
    dim = model.f.get_dimension()
    return User(user_id=user_id, user_vector=zeros(dim))


def user_exists(user_id):
    if user_id:
        return len(User.objects(user_id=user_id)) > 0
    return False


def find_user(user_id):
    return User.objects.get(user_id=user_id)


def delete_user(user_id):
    return find_user(user_id).objects.delete()


def get_current_user_id():
    from flask import request
    if "_ga" in request.cookies:
        user_id = request.cookies.get("_ga")
        return user_id
    return None


def create_session(user, session_id):
    assert isinstance(user, User), "Must supply instance of User"
    return Session(user_id=user.id, session_id=session_id)


def get_current_session_id():
    from flask import request
    if "_gid" in request.cookies:
        session_id = request.cookies.get("_gid")
        return session_id
    return None


def session_exits(user, session_id):
    assert isinstance(user, User), "Must supply instance of User"
    if session_id:
        return len(Session.objects(user_id=user.id, session_id=session_id)) > 0
    return False


def get_current_session(user=get_current_user()):
    assert isinstance(user, User), "Must supply instance of User"
    session_id = get_current_session_id()
    if session_id:
        if session_exits(session_id):
            return Session.objects.get(user_id=user.id, session_id=session_id)
        else:
            session = create_session(user, session_id)
            session.save()
            return session
    return None


def get_sessions_for_user(user=get_current_user()):
    assert isinstance(user, User), "Must supply instance of User"
    return Session.objects(user_id=user.id)


def get_latest_session(user=get_current_user()):
    assert isinstance(user, User), "Must supply instance of User"

    # Search for sessions with this users id and sort by descending order based on ObjectId (-id)
    # Note - in mongoDB the ObjectId also serves as a timestamp
    sessions = get_sessions_for_user(user).order_by("-id")
    if len(sessions) > 0:
        return sessions[0]
    return None