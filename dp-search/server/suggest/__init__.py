from flask import Blueprint

# Create the suggest blueprint
suggest = Blueprint("suggest", __name__)

from . import routes