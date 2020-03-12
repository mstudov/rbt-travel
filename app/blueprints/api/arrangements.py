from app.extensions import db

from flask import (
    g,
    jsonify,
    render_template,
    request,
    redirect,
    flash,
    url_for
)

from flask_login import current_user, login_required

from app.extensions import db, basic_auth, token_auth
from app.blueprints.api import blueprint
from app.blueprints.api.errors import error_response, bad_request
from app.blueprints.api.permissions import requires_role, Role
from app.models import TravelArrangement#, GuideUser, \
#    TravelArrangementTouristUser
#from app.permissions import Role, requires_role

@blueprint.route('/arrangements', methods=['GET'])
@token_auth.login_required
def get_arrangements():
    page = request.args.get('page', 1, type=int)
    per_page = min(request.args.get('per_page', 10, type=int), 100)
    results = TravelArrangement.to_collection_dict(
        TravelArrangement.query,
        page,
        per_page,
        'api.get_arrangements')
    return jsonify(results)

@blueprint.route('/arrangements/<int:id>', methods=['GET'])
@token_auth.login_required
def get_arrangement(id):
    return  jsonify(TravelArrangement.query.get_or_404(id).to_dict())

@blueprint.route('/arrangements', methods=['POST'])
@token_auth.login_required
@requires_role(roles=[Role.ADMIN])
def create_arrangement():
    data = request.get_json() or {}
    if 'location' not in data or 'price' not in data or \
       'total_spots' not in data or 'start_date' not in data or \
       'end_date' not in data:
        return bad_request("must include location, price, total_spots, " \
                           "start_date and end_date")
    arrangement = TravelArrangement()
    arrangement.from_dict(data)
    arrangement.admin_id = g.current_user.get_admin().id
    db.session.add(arrangement)
    db.session.commit()
    response = jsonify(arrangement.to_dict())
    response.status_code = 201
    return response
#
@blueprint.route('/arrangements/<int:id>', methods=['PUT'])
@token_auth.login_required
def update_arrangement(id):
    #return str(request.json.get('username', None))
    return 'update {} arrangement'.format(id)

@blueprint.route('/arrangements/<int:id>', methods=['DELETE'])
@token_auth.login_required
def delete_arrangement(id):
    return 'delete {} arrangement'.format(id)

@blueprint.route('/arrangements/<int:id>/book', methods=['G'])
@token_auth.login_required
def book_arrangement(id):
    return 'book {} arrangement'.format(id)

@blueprint.route('/arrangements/<int:id>/guide_position', methods=['POST'])
@token_auth.login_required
def request_guide_position(id):
    arrangement_id = request.args.get('arrangement_id', None, type=int)
    return 'request guide position for {} arrangement'.format(id)

@blueprint.route('/arrangements/<int:id>/guide_position', methods=['PUT'])
@token_auth.login_required
def approve_request_guide_position(id):
    guide_id = request.args.get('guide_id', None, type=int)
    return 'request guide position for {} arrangement'.format(id)
