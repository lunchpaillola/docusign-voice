from flask import Blueprint
dataio = Blueprint('dataio', __name__)

from . import routes  # Register routes 