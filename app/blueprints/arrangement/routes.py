from app.extensions import db

from flask import (
    render_template,
    request,
    redirect,
    flash,
    url_for
)

from flask_login import current_user, login_required

from app.extensions import db
from app.blueprints.arrangement import blueprint
from app.blueprints.arrangement.forms import CreateArrangementForm, BookArrangementForm
#from app.arrangement.models import TravelArrangement, GuideUser, \
#    TravelArrangementTouristUser
from app.models import TravelArrangement, GuideUser, \
    TravelArrangementTouristUser
from app.permissions import Role, requires_role

@blueprint.route('/create/', methods=['GET', 'POST'])
@login_required
@requires_role(roles=[Role.ADMIN])
def create_arrangement():
    form = CreateArrangementForm()
    if form.validate_on_submit():
        arrang = TravelArrangement(start_date=form.start_date.data,
           end_date=form.end_date.data,
           description=form.description.data,
           location=form.location.data,
           price=form.price.data,
           avl_spots=form.avl_spots.data,
           admin_id=current_user.get_admin().id)
        if form.guide.data != -1:
            arrang.guide_id = form.guide.data
        db.session.add(arrang)
        db.session.commit()
        flash('New travel arrangement created.')
        return redirect(url_for('main.index'))
    return render_template('arrangement/create_arrangement.html', form=form)

@blueprint.route('/<int:id>/edit/', methods=['GET', 'POST'])
@login_required
@requires_role(roles=[Role.GUIDE, Role.ADMIN])
def edit_arrangement(id):
    arrang = TravelArrangement.query.filter_by(id=id).first_or_404()
    if arrang.admin.user != current_user and arrang.guide.user != current_user:
        flash('You did not create this arrangement.')
        return redirect(url_for('main.index'))

    form = CreateArrangementForm()
    form.submit.label.text = 'Save'

    if form.validate_on_submit():
        if current_user.is_admin():
            arrang.start_date = form.start_date.data
            arrang.end_date = form.end_date.data
            arrang.location = form.location.data
            arrang.price = form.price.data
            arrang.avl_spots = form.avl_spots.data
            arrang.guide_id = form.guide.data if form.guide.data != -1 else None
        arrang.description = form.description.data
        db.session.commit()
        flash('Success! Updated arrangement details.')
        return redirect(url_for('main.index'))
    elif request.method == 'GET':
        if current_user.is_admin():
            form.start_date.data = arrang.start_date
            form.end_date.data = arrang.end_date
            form.location.data = arrang.location
            form.price.data = arrang.price
            form.avl_spots.data = arrang.avl_spots
            form.guide.data = arrang.guide.id if arrang.guide is not None \
                else -1
        form.description.data = arrang.description
    return render_template('arrangement/create_arrangement.html', form=form)

@blueprint.route('/<int:id>/delete/')
@login_required
@requires_role(roles=[Role.ADMIN])
def delete_arrangement(id):
    arrang = TravelArrangement.query.filter_by(id=id).first_or_404()
    if arrang.admin.user.id != current_user.id:
        flash('You can\'t modify arrangement that you didn\'t created!')
        return redirect(url_for('main.unauthorized'))

    # TODO: TravelArrangementTouristUser records too
    arrang.notify_users_deletion()
    # deletes Tourist<->TravelArrangement many-to-many table rows
    for t in arrang._tourists:
        db.session.delete(t)
    db.session.delete(arrang)
    db.session.commit()
    flash('Arrangement was deleted.')
    return redirect(url_for('main.index'))

@blueprint.route('/<int:id>/')
@login_required
def view_arrangement(id):
    arrang = \
        TravelArrangement.query.filter_by(id=id).first_or_404()
    return render_template('arrangement/view_arrangement.html', arrang=arrang)

@blueprint.route('/<int:id>/book/', methods=['GET', 'POST'])
@login_required
@requires_role(roles=[Role.TOURIST])
def book_arrangement(id):
    arrang = TravelArrangement.query.filter_by(id=id).first_or_404()
    form = BookArrangementForm()
    if form.validate_on_submit():
        # TODO: Check if it is booked already.
        # display only un-booked arrangements
        price = current_user.get_tourist().book(
                    arrang, form.book_spots.data)
        flash('Arrangement to {} booked. Total price is {:.2f}.'.format(
            arrang.location,
            price))
        return redirect(url_for('main.index'))
    return render_template('arrangement/book_arrangement.html', form=form, arrangement=arrang)

@blueprint.route('/<int:id>/guide/')
@login_required
@requires_role(roles=[Role.GUIDE, Role.ADMIN])
def request_guide_position(id):
    arrang = TravelArrangement.query.filter_by(id=id).first_or_404()
    # requesting to be a guide
    if current_user.is_guide():
        current_user.get_guide().request_guide_position(arrang)
        flash('Guide request for a travel arrangement to {} submitted.'.format(
            arrang.location))
        return redirect(url_for('main.index'))
    # approving the guide
    elif arrang.admin.user == current_user:
        guide = GuideUser.query.filter_by(
            id=request.args.get('guide_id', None, type=int)).first_or_404()
        arrang.guide_id = guide.id
        db.session.commit()
        user = guide.user
        flash('{} {} is a new guide for a travel arrangement to {}.'.format(
            user.first_name, user.last_name, arrang.location))
        return redirect(url_for('main.index'))
    else:
        flash('You can\'t modify arrangement that you didn\'t created!')
        return redirect(url_for('main.unauthorized'))

@blueprint.route('/all/guide/')
@login_required
@requires_role(roles=[Role.ADMIN])
def approve_guide_requests():
#def arrangement_guide_approve():
    arrangs = current_user.get_admin().get_arrangements()
    return render_template('arrangement/approve_guide_requests.html', arrangements=arrangs)
