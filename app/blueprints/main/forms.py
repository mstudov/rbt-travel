from flask_wtf import FlaskForm

from wtforms import (
    StringField,
    BooleanField,
    SubmitField,
    DateTimeField,
)
#from wtforms.validators import DataRequired

class FilterArrangementsForm(FlaskForm):
    destination = StringField('Destination')
    start_date = DateTimeField('Start date')
    admin_own_arrangements = BooleanField('My arrangements')
    admin_no_guide_arrangements = BooleanField('Missing guides')
    search = SubmitField('Search')
    reset = SubmitField('Reset')
