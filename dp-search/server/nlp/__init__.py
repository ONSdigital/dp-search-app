from flask import Blueprint

# Create the nlp blueprint
nlp = Blueprint("nlp", __name__)

from . import routes