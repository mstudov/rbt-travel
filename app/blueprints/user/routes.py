from flask import (
    current_app,
    render_template,
    request,
    redirect,
    flash,
    url_for
)

from flask_login import current_user, login_required

from app.extensions import db
from app.blueprints.user import blueprint
from app.blueprints.user.forms import NewUserForm, EditProfileForm
#from app.user.models import User, TouristUser, AdminUser, GuideUser
from app.models import (
    User,
    TouristUser,
    AdminUser,
    GuideUser,
    TravelArrangement,
    TravelArrangementTouristUser
)
from app.permissions import Role, requires_role

@blueprint.route('/create/', methods=['GET', 'POST'])
@login_required
@requires_role(roles=[Role.ADMIN])
def create_user():
    form = NewUserForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data,
            first_name=form.first_name.data, last_name=form.last_name.data)
        user.set_password(form.password.data)
        user.set_role(form.user_role.data)
        db.session.add(user)
        db.session.flush()
        if form.user_role.data == Role.TOURIST:
            db.session.add(TouristUser(user_id=user.id))
        elif form.user_role.data == Role.GUIDE:
            db.session.add(GuideUser(user_id=user.id))
        elif form.user_role.data == Role.ADMIN:
            db.session.add(AdminUser(user_id=user.id))
        db.session.commit()
        flash('New user "{}" created!'.format(user.username))
        #return redirect(url_for('main.new_user'))
    return render_template('user/new_user.html', form=form)

@blueprint.route('/', defaults={'id': None})
@blueprint.route('/<int:id>/')
@login_required
def view_profile(id):
    user = User.query.filter_by(id=id).first_or_404() if id is not None \
        else current_user

    # TODO: Use relationships instead of manually quering the database
    if user == current_user and current_user.is_tourist():
        #arrangs = user.get_tourist().arrangements
        arrangs = TravelArrangement.query.join(
            TravelArrangementTouristUser,
            TravelArrangementTouristUser.\
                travel_arrangement_id==TravelArrangement.id).filter(
                    TravelArrangementTouristUser.\
                        tourist_user_id==current_user.get_tourist().id).\
                            order_by(TravelArrangement.start_date.desc())
    elif user == current_user and current_user.is_guide():
        #arrangs = user.get_guide().arrangements
        arrangs = TravelArrangement.query.join(
            GuideUser, TravelArrangement.guide_id==GuideUser.id).order_by(
                TravelArrangement.start_date.desc())
    else:
        arrangs = None
        next_url = None
        prev_url = None

    if arrangs:
        page = request.args.get('page', 1, type=int)
        arrangs = arrangs.paginate(
            page,
            current_app.config['RESULTS_PER_PAGE'],
            False)
        next_url = url_for('user.view_profile', page=arrangs.next_num) \
            if arrangs.has_next else None
        prev_url = url_for('user.view_profile', page=arrangs.prev_num) \
            if arrangs.has_prev else None
        arrangs = arrangs.items

    return render_template('user/view_user.html', 
                           user=user,
                           arrangements=arrangs,
                           next_url=next_url, prev_url=prev_url)

@blueprint.route('/edit/', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm()
    user = current_user
    if form.validate_on_submit():
        user.username = form.username.data
        user.first_name = form.first_name.data
        user.last_name = form.last_name.data
        user.email = form.email.data
        db.session.commit()
        flash('Successfully updated user information!')
    elif request.method == 'GET':
        form.username.data = user.username
        form.first_name.data = user.first_name
        form.last_name.data = user.last_name
        form.email.data = user.email
    return render_template('user/edit_profile.html', form=form, user=current_user)
