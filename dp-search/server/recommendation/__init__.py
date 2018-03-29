from flask import Blueprint

# Create the suggest blueprint
recommendation = Blueprint("recommendation", __name__)

from . import routes
