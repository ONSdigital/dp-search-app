from numpy import zeros
from user import model, User, Session


class UserUtils():
    @staticmethod
    def create_user(user_id):
        return User(user_id=user_id)

    @staticmethod
    def user_exists(user_id):
        if user_id:
            return len(User.objects(user_id=user_id)) > 0
        return False

    @staticmethod
    def find_user(user_id):
        return User.objects.get(user_id=user_id)

    @staticmethod
    def delete_user(user_id):
        return UserUtils.find_user(user_id).objects.delete()

    @staticmethod
    def get_current_user_id():
        from flask import request
        if "_ga" in request.cookies:
            user_id = request.cookies.get("_ga")
            return user_id
        return None

    @staticmethod
    def get_current_user():
        user_id = UserUtils.get_current_user_id()
        if user_id:
            if UserUtils.user_exists(user_id):
                return UserUtils.find_user(user_id)
            else:
                # Create a user
                user = UserUtils.create_user(user_id)

                # Save the user
                user.save()
                return user
        return None


class SessionUtils():
    """
    TODO - Test query logic here to make sure sessions aren't being deserialised for no reason
    """
    @staticmethod
    def create_session(user, session_id):
        assert isinstance(user, User), "Must supply instance of User"

        dim = model.f.get_dimension()
        return Session(user_id=user.id, session_id=session_id, session_vector=zeros(dim))

    @staticmethod
    def get_current_session_id():
        from flask import request

        if "_gid" in request.cookies:
            session_id = request.cookies.get("_gid")
            return session_id
        return None

    @staticmethod
    def session_exits(user, session_id):
        assert isinstance(user, User), "Must supply instance of User"

        if session_id:
            return len(Session.objects(user_id=user.id, session_id=session_id)) > 0
        return False

    @staticmethod
    def get_sessions_for_user(user=UserUtils.get_current_user()):
        assert isinstance(user, User), "Must supply instance of User"

        num_sessions = Session.objects(user_id=user.id).count()
        if num_sessions == 0:
            session = SessionUtils.get_current_session(user)
            if session:
                session.save()
        return Session.objects(user_id=user.id)

    @staticmethod
    def get_latest_session(user=UserUtils.get_current_user()):
        assert isinstance(user, User), "Must supply instance of User"

        # Search for sessions with this users id and sort by descending order based on ObjectId (-id)
        # Note - in mongoDB the ObjectId also serves as a timestamp
        sessions = SessionUtils.get_sessions_for_user(user).order_by("-id")
        if len(sessions) > 0:
            return sessions[0]
        return None

    @staticmethod
    def get_current_session(user=UserUtils.get_current_user()):
        assert isinstance(user, User), "Must supply instance of User"

        session_id = SessionUtils.get_current_session_id()
        if session_id:
            if SessionUtils.session_exits(user, session_id):
                return Session.objects.get(user_id=user.id, session_id=session_id)
            else:
                session = SessionUtils.create_session(user, session_id)
                session.save()
                return session
        return None
