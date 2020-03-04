import datetime
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, \
    DateTimeField, TextAreaField, IntegerField, SelectField
from wtforms.validators import ValidationError, DataRequired, EqualTo, Email
from app.models import User, GuideUser
from app.permissions import Role

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember me')
    submit = SubmitField('Login')

class CreateArrangementForm(FlaskForm):
    start_date = DateTimeField('Start date',
                               format='%d-%m-%Y',
                               validators=[DataRequired()])
    end_date = DateTimeField('End date', 
                             format='%d-%m-%Y',
                             validators=[DataRequired()])
    description = TextAreaField('Description')
    location = StringField('Location', validators=[DataRequired()]) 
    price = IntegerField('Price', validators=[DataRequired()]) 
    avl_spots = IntegerField('Available spots', validators=[DataRequired()]) 
    guide = SelectField('Select guide', coerce=int) 
    submit = SubmitField('Create')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not self.start_date.data:
            self.start_date.data = datetime.date.today()
        if not self.end_date.data:
            self.end_date.data = datetime.date.today()
        self.guide.choices = [(-1, '-None-')]
        self.guide.choices += [(guide.id,
                               "{} {} ({})".format(guide.user.first_name,
                                                   guide.user.last_name,
                                                   guide.user.first_name,
                                                   guide.user.username)) \
                                        for guide in GuideUser.query.all()]

    def validate_start_date(self, start_date):
        return
        if start_date > self.end_date:
            raise ValidationError('Start date can\'t be higher than end date.')
        
class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    first_name = StringField('First Name', validators=[DataRequired()])
    last_name = StringField('Last Name', validators=[DataRequired()])
    email = StringField('E-Mail', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField(
        'Repeat Password', validators=[DataRequired(), EqualTo('password')])
    admin = BooleanField('Admin?')
    submit = SubmitField('Register')

    # TODO: refactor. not the best practice ever to re-use code like this
    #user_type = SelectionField('User type', validators=[DataRequired()])

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Please use a different username.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Please use a different email.')

class FilterArrangementsForm(FlaskForm):
    destination = StringField('Destination')
    start_date = DateTimeField('Start date')
    admin_own_arrangements = BooleanField('My arrangements')
    admin_no_guide_arrangements = BooleanField('Missing guides')
    search = SubmitField('Search')
    reset = SubmitField('Reset')

class EditProfileForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    first_name = StringField('First Name', validators=[DataRequired()])
    last_name = StringField('Last Name', validators=[DataRequired()])
    email = StringField('E-Mail', validators=[DataRequired(), Email()])
    submit = SubmitField('Save')

class NewUserForm(RegistrationForm):
    user_role = SelectField('User role', 
                            coerce=int,
                            default=0)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.submit.label.text = 'Create new user'
        self.user_role.choices = [
            (Role.TOURIST, 'Tourist'),
            (Role.GUIDE, 'Guide'),
            (Role.ADMIN, 'Admin')]

class BookArrangementForm(FlaskForm):
    book_spots = IntegerField('Number of spots', validators=[DataRequired()])
    submit = SubmitField('Book arrangement')
