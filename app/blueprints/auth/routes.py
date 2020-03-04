from flask import (
    render_template,
    redirect,
    flash,
    url_for,
    request
)

from flask_login import current_user, login_user, logout_user

from app.extensions import db
from app.blueprints.auth import blueprint
from app.blueprints.auth.forms import LoginForm, RegistrationForm
#from app.auth.models import User, TouristUser
from app.models import User, TouristUser
from app.permissions import Role

@blueprint.route('/register/', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data,
            first_name=form.first_name.data, last_name=form.last_name.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.flush()
        #if form.admin.data: # debug code
        #    user.set_role(Role.ADMIN)
        #    db.session.add(AdminUser(user_id=user.id))
        #else:
        user.set_role(Role.TOURIST)
        db.session.add(TouristUser(user_id=user.id))
        db.session.commit()
        flash('Registration successful!')
        return redirect(url_for('auth.login'))
    return render_template('auth/register.html', title='Registration', form=form)

@blueprint.route('/login/', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('auth.login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next') or url_for('main.index')
        return redirect(next_page)
    return render_template('auth/login.html', title='Login', form=form)

@blueprint.route('/logout/')
def logout():
    logout_user()
    return redirect(url_for('main.index'))
