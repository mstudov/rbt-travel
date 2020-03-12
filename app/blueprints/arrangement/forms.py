import datetime
from flask_wtf import FlaskForm
from wtforms import (
    StringField,
    SubmitField,
    DateTimeField,
    TextAreaField,
    IntegerField,
    SelectField
)
from wtforms.validators import ValidationError, DataRequired
from app.models import GuideUser

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
    total_spots = IntegerField('Total spots', validators=[DataRequired()]) 
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
        
class BookArrangementForm(FlaskForm):
    book_spots = IntegerField('Number of spots', validators=[DataRequired()])
    submit = SubmitField('Book arrangement')
