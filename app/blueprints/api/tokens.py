from flask import jsonify, g

from app.extensions import db, basic_auth
from app.blueprints.api import blueprint

@blueprint.route('/tokens', methods=['POST'])
@basic_auth.login_required
def get_token():
    token = g.current_user.get_token()
    db.session.commit()
    return jsonify({'token': token})

@blueprint.route('/tokens', methods=['DELETE'])
def revoke_token():
    g.current_user.revoke_token()
    db.session.commit()
    return '', 204
