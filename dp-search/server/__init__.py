import os
import logging
from flask import Flask, request, jsonify
from time import strftime


def _create_app():
    from search.engine import search_url
    from logging.handlers import RotatingFileHandler
    # Initialise the app
    config_name = os.environ.get('FLASK_CONFIG', 'development')

    app = Flask(__name__, template_folder="../web/templates", static_folder="../web/static")
    app.config.from_object('config_' + config_name)

    # Setup logging
    file_handler = RotatingFileHandler(
        'dp-search-app.log', maxBytes=1024 * 1024 * 100, backupCount=3)
    file_handler.setLevel(logging.ERROR)
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    file_handler.setFormatter(formatter)
    app.logger.addHandler(file_handler)

    # Import blueprints
    from .search import search as search_blueprint
    from .suggest import suggest as suggest_blueprint

    # Register blueprints
    app.register_blueprint(search_blueprint, url_prefix="/search")
    app.register_blueprint(suggest_blueprint, url_prefix="/suggest")

    # Log some setup variables
    app.logger.info("Running in %s mode" % config_name)
    app.logger.info("Elasticsearch url: %s" % search_url)

    # Init suggest models using app config
    from suggest import word2vec_models, supervised_models
    word2vec_models.init(app)
    supervised_models.init(app)

    return app


# Create the app
app = _create_app()


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


@app.errorhandler(Exception)
def internal_server_error(exception):
    """ Define a custom error handler that guarantees exceptions are always logged. """
    # Log the exception
    import sys, traceback
    from utils import is_number

    type_, value_, traceback_ = sys.exc_info()
    app.logger.error(str(traceback.format_tb(traceback_)) + "\n")
    # Jsonify the exception and return a error response
    response = jsonify({
            "type": str(type_),
            "value": str(value_),
            "traceback": traceback.format_tb(traceback_)
        })
    if hasattr(exception, "status_code") and is_number(exception.status_code):
        response.status_code = int(exception.status_code)
    else:
        response.status_code = 500
    return response
