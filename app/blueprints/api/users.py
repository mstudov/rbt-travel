from app.extensions import db

from flask import (
    current_app,
    render_template,
    request,
    redirect,
    flash,
    url_for
)

from flask_login import current_user, login_required

from app.extensions import db, basic_auth
from app.blueprints.api import blueprint
from app.blueprints.api.errors import bad_request
#from app.models import TravelArrangement, GuideUser, \
#    TravelArrangementTouristUser
#from app.permissions import Role, requires_role

@blueprint.route('/users', methods=['GET'])
def get_users():
    pass

@blueprint.route('/users/<int:id>', methods=['GET'])
def get_user(id):
    pass

@blueprint.route('/users', methods=['POST'])
def create_user():
    if 'username' not in data or 'email' not in data or \
       'first_name' not in data or 'last_name' not in data:
        bad_request('ni sam djavo ne bi')
    if g.current_user and g.current_user.is_admin():
        pass

@blueprint.route('/users/<int:id>', methods=['PUT'])
def update_user(id):
    pass
