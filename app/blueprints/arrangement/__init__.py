from flask import Blueprint

blueprint = Blueprint('arrangement', __name__, url_prefix='/arrangements')

from app.blueprints.arrangement import routes
