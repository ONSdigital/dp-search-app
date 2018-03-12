import os
import logging
from flask import Flask
from flask import request
from flask import jsonify
from time import strftime


def _create_app():
    from search.engine import search_url
    from logging.handlers import RotatingFileHandler
    # Initialise the app
    config_name = os.environ.get('FLASK_CONFIG', 'development')

    app = Flask(__name__)
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
    app.register_blueprint(search_blueprint, url_prefix="/search")

    # Log some setup variables
    app.logger.info("Running in %s mode" % config_name)
    app.logger.info("Elasticsearch url: %s" % search_url)

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
    from utils import is_number
    app.logger.error(exception)
    # Jsonify the exception and return a error response
    response = jsonify({"message": str(exception)})
    if (hasattr(exception, "status_code") and is_number(exception.status_code)):
        response.status_code = int(exception.status_code)
    else:
        response.status_code = 500
    return response
