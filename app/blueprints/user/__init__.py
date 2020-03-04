from flask import Blueprint

blueprint = Blueprint('user', __name__, url_prefix='/users')

from app.blueprints.user import routes
