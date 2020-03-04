from flask import (
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
from app.models import User, TouristUser, AdminUser, GuideUser
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

    arrangs = None
    if user == current_user and current_user.is_tourist():
        arrangs = user.get_tourist().arrangements
    elif user == current_user and current_user.is_guide():
        # TODO: Returns query, not results ?! lazy='dynamic' !!!
        arrangs = user.get_guide().arrangements

    return render_template('user/view_user.html', 
                           user=user,
                           arrangements=arrangs)

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
