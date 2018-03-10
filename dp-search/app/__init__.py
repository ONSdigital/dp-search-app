import os
from flask import Flask
from flask_cors import CORS


def create_app():
    config_name = os.environ.get('FLASK_CONFIG', 'development')

    app = Flask(__name__)
    app.config.from_object('config_' + config_name)

    CORS(app)

    from .search import search as search_blueprint
    app.register_blueprint(search_blueprint)

    return app
