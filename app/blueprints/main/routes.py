from flask import (
    current_app,
    render_template,
    request,
    redirect,
    url_for
)

from flask_login import current_user

from app.blueprints.main import blueprint
from app.blueprints.main.forms import FilterArrangementsForm
#        from app.main.models import TravelArrangement, AdminUser
from app.models import TravelArrangement, AdminUser

#from datetime import datetime

@blueprint.route('/', methods=['GET', 'POST'])
@blueprint.route('/index/', methods=['GET', 'POST'])
def index():
    form = FilterArrangementsForm()
    if form.validate_on_submit():
        if 'search' in request.form:
            # TODO: Implement keyword based search functionality
            if form.admin_own_arrangements.data:
                arrangs = current_user.get_admin().arrangements
                #arrangs = AdminUser.query.filter_by(user_id=current_user.id) \
                #    .first().arrangements
                #    #.first().arrangements
            else:
                arrangs = TravelArrangement.query \
                    .order_by(TravelArrangement.start_date.desc())
                #if current_user.is_tourist():
                #    arrangs = arrangs \
                #        .filter(TravelArrangement.start_date > datetime.utcnow()).all()
        elif 'reset' in request.form:
            form.search.data = ''
            form.admin_own_arrangements.data = False
            form.admin_no_guide_arrangements.data = False
            return redirect(url_for('main.index'))
    elif request.method == 'GET':
        if current_user.is_anonymous or current_user.is_admin():
            arrangs = TravelArrangement.query.order_by(
                TravelArrangement.start_date.desc())
        elif current_user.is_tourist():
            arrangs = current_user.get_tourist().get_arrangements_query()
        elif current_user.is_guide():
            arrangs = current_user.get_guide().get_arrangements_query()

        page = request.args.get('page', 1, type=int)
        arrangs = arrangs.paginate(page,
            current_app.config['RESULTS_PER_PAGE'], False)
        next_url = url_for('main.index', page=arrangs.next_num) \
            if arrangs.has_next else None
        prev_url = url_for('main.index', page=arrangs.prev_num) \
            if arrangs.has_prev else None
    return render_template('main/index.html', form=form,
        arrangements=arrangs.items, next_url=next_url, prev_url=prev_url)

@blueprint.route('/unauthorized/')
def unauthorized():
    return redirect(url_for('main.index'))
