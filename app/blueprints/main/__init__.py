from flask import Blueprint

blueprint = Blueprint('main', __name__)

from app.blueprints.main import routes
