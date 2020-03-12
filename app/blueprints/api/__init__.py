from flask import Blueprint

blueprint = Blueprint('api', __name__, url_prefix='/api')

from app.blueprints.api import (
    auth,
    arrangements,
    users,
    errors,
    tokens
)
