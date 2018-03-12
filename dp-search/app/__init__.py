import os
import logging
from flask import Flask, request
from flask import render_template
from flask_cors import CORS
from time import strftime

def _create_app():
    from logging.handlers import RotatingFileHandler
    # Initialise the app
    config_name = os.environ.get('FLASK_CONFIG', 'development')

    app = Flask(__name__)
    app.config.from_object('config_' + config_name)

    # Enable Cross Origin Resource Sharing
    CORS(app)

    # Setup logging
    file_handler = RotatingFileHandler('dp-search-app.log', maxBytes=1024 * 1024 * 100, backupCount=3)
    file_handler.setLevel(logging.ERROR)
    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    file_handler.setFormatter(formatter)
    app.logger.addHandler(file_handler)

    # Import blueprints
    from .search import search as search_blueprint
    app.register_blueprint(search_blueprint, url_prefix="/search")

    return app

# Create the app
app = _create_app()

# Log after every request
@app.after_request
def after_request(response):
    """ Logging after every request. """
    # This avoids the duplication of registry in the log,
    # since that 500 is already logged via @app.errorhandler.
    if response.status_code != 500:
        ts = strftime('[%Y-%b-%d %H:%M]')
        app.logger.info('%s %s %s %s %s %s',
                      ts,
                      request.remote_addr,
                      request.method,
                      request.scheme,
                      request.full_path,
                      response.status)
    return response

# Define a custom error handler that guarantees exceptions are always logged
@app.errorhandler(Exception)
def internal_server_error(exception):
    # Log the exception
    app.logger.error(exception)
    # Return the error page
    return exception, 500
