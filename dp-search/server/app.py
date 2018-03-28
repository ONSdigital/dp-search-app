import logging
import os
from time import strftime

from flask import Flask
from flask import request, redirect, jsonify

from exceptions.requests import BadRequest


def get_request_param(key, required, default=None):
    """
    Simple util function for extracting parameters from requests.
    :param key:
    :param required:
    :param default:
    :return: value
    :raises ValueError: key not found or value is None
    """
    if key in request.args:
        value = request.args.get(key)
        if value is not None and len(value) > 0:
            return value
    if required:
        message = "Invalid value for required argument '%s' and route '%s'" % (key, request.url)
        # Will be automatically caught by handle_exception and return a 400
        raise BadRequest(message)
    else:
        return default


def create_app():
    from response import AutoJSONEncoder
    from search.search_engine import search_url
    from logging.handlers import RotatingFileHandler

    # Get the config name
    config_name = os.environ.get('FLASK_CONFIG', 'development')

    # Initialise the app from the config
    app = Flask(__name__, template_folder="../web/templates", static_folder="../web/static")
    app.config.from_object('config_' + config_name)

    # Set custom JSONEncoder
    app.json_encoder = AutoJSONEncoder

    # Setup logging
    file_handler = RotatingFileHandler(
        'dp-search-app.log', maxBytes=1024 * 1024 * 100, backupCount=3)
    file_handler.setLevel(logging.ERROR)
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    file_handler.setFormatter(formatter)
    app.logger.addHandler(file_handler)

    app.logger.info("Initialising application from config '%s'" % config_name)

    # Import blueprints
    from .search import search as search_blueprint
    from .suggest import suggest as suggest_blueprint
    from .nlp import nlp as nlp_blueprint

    # Register blueprints
    app.register_blueprint(search_blueprint, url_prefix="/search")
    app.register_blueprint(suggest_blueprint, url_prefix="/suggest")
    app.register_blueprint(nlp_blueprint, url_prefix="/nlp")

    # Log some setup variables
    app.logger.info("Elasticsearch url: %s" % search_url)

    # Init suggest models using app config
    from suggest import word2vec_models, supervised_models
    word2vec_models.init(app)
    supervised_models.init(app)

    # Redirect from index to apidocs
    @app.route("/")
    def index():
        return redirect("/apidocs")

    # Declare function to log each request
    @app.after_request
    def after_request(response):
        from users.user import create_user, user_exists

        """ Logging after every request. """
        # This avoids the duplication of registry in the log,
        # since that 500 is already logged via @app.errorhandler.
        if response.status_code != 500:
            ts = strftime('[%Y-%b-%d %H:%M]')
            app.logger.info('%s %s %s %s %s %s %s',
                            ts,
                            request.remote_addr,
                            request.method,
                            request.scheme,
                            request.full_path,
                            request.cookies,
                            response.status)

        # Track the user
        if "_ga" in request.cookies:
            user_id = request.cookies.get("_ga")
            if not user_exists(user_id):
                app.logger.info("Creating user: %s" % user_id)
                user = create_user(user_id)
                try:
                    user.save()
                    app.logger.info("User '%s' saved" % user_id)
                except Exception as e:
                    app.logger.error("Unable to create user '%s'" % user_id, e)
        return response

    # Declare function to log all uncaught exceptions and return a 500 with info
    @app.errorhandler(Exception)
    def handle_exception(exception):
        """ Define a custom error handler that guarantees exceptions are always logged. """
        # Log the exception
        import sys
        import traceback
        from utils import is_number

        type_, value_, traceback_ = sys.exc_info()
        err = {
            "type": str(type_),
            "value": str(value_),
            "traceback": traceback.format_tb(traceback_)
        }
        if app.config["TESTING"] is False:
            app.logger.error(str(err) + "\n")
        # Jsonify the exception and return a error response
        response = jsonify(err)
        if hasattr(exception, "status_code") and is_number(exception.status_code):
            response.status_code = int(exception.status_code)
        else:
            response.status_code = 500
        return response

    return app
