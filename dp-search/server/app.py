import os
from time import strftime

from flask import Flask
from flask import request, redirect, jsonify

from requests.requests import CustomRequest
from .search import search as search_blueprint

# Get the config name
config_name = os.environ.get('FLASK_CONFIG', 'development')


class CustomFlask(Flask):
    request_class = CustomRequest


def initialise_app_with_logger():
    import logging
    from response import AutoJSONEncoder
    from logging.handlers import RotatingFileHandler

    # Initialise the app from the config
    app = CustomFlask(
        __name__,
        template_folder="../web/templates",
        static_folder="../web/static")
    app.config.from_object('config_' + config_name)

    # Setup logging
    file_handler = RotatingFileHandler(
        'dp-search-app.log', maxBytes=1024 * 1024 * 100, backupCount=3)
    file_handler.setLevel(logging.ERROR)
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    file_handler.setFormatter(formatter)
    app.logger.addHandler(file_handler)

    if config_name == "production":
        app.logger.setLevel(logging.ERROR)

    app.logger.info("Initialising application from config '%s'" % config_name)

    # Set custom JSONEncoder
    app.json_encoder = AutoJSONEncoder

    # Enable CORS?
    if os.environ.get('FLASK_CORS', 'False') == "True":
        from flask_cors import CORS
        CORS(app)

    # Init response compression?
    if os.environ.get('FLASK_COMPRESSION', 'True') == "True":
        from flask_compress import Compress
        Compress(app)

    return app


def create_app():
    from search.search_engine import search_url
    app = initialise_app_with_logger()

    # Import blueprints
    # Register blueprints
    app.register_blueprint(search_blueprint, url_prefix="/search")

    # Search only?
    search_only = os.environ.get('SEARCH_ONLY', 'False') == "True"
    app.config["SEARCH_ONLY"] = search_only

    if app.config["SEARCH_ONLY"] is False:
        from flask_mongoengine import MongoEngine

        app.logger.info("Initialising additional endpoints")

        # Init mongoDB connection
        app.db = MongoEngine(app)
        app.logger.info("MongoDB initialised")

        # Init suggest models using app config
        from word_embedding import word2vec_models, supervised_models
        word2vec_models.init(app)
        supervised_models.init(app)

        # Register API blueprints
        from .suggest import suggest as suggest_blueprint
        from .recommendation import recommendation as recommendation_blueprint

        app.register_blueprint(suggest_blueprint, url_prefix="/suggest")
        app.register_blueprint(
            recommendation_blueprint,
            url_prefix="/recommend")

    # Log some setup variables
    app.logger.info("Elasticsearch url: %s" % search_url)

    from flasgger import Swagger
    if config_name == "development":
        # Init swagger API docs
        Swagger(app)
        app.logger.info("Swagger API docs initialised")

        # Redirect from index to apidocs
        @app.route("/")
        def index():
            return redirect("/apidocs")

    # Declare function to log each request
    @app.after_request
    def after_request(response):
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
        return response

    # Declare function to log all uncaught exceptions and return a 500 with
    # info
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
        # Jsonify the exception and return a error response
        response = jsonify(err)
        if hasattr(
                exception,
                "status_code") and is_number(
            exception.status_code):
            response.status_code = int(exception.status_code)
        else:
            response.status_code = 500
            if app.config["TESTING"] is False:
                app.logger.error(str(err) + "\n")
        return response

    return app
