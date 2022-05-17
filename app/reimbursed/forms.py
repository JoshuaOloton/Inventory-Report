from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField, IntegerField
from wtforms.validators import InputRequired, Length, NumberRange

class NewInventoryForm(FlaskForm):
    item = StringField('Name of Item',validators=[InputRequired(), Length(max=20)])
    units = IntegerField('No of Units',validators=[InputRequired(), NumberRange(min=1,message='Invalid no of units')])
    description =TextAreaField('Description',validators=[Length(max=1000)])
    submit = SubmitField('Add Item')