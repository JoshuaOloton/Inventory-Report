from xml.dom import ValidationErr
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField, DateTimeField, IntegerField, SelectField
from wtforms.validators import InputRequired, Length, NumberRange
from app.models import InStock
from wtforms.fields.html5 import DateField

class ChooseDateForm(FlaskForm):
    start_date = DateField('Start Date')
    end_date = DateField('End Date')
    submit = SubmitField('View Report')

