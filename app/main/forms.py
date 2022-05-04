from xml.dom import ValidationErr
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField, DateTimeField, IntegerField, SelectField
from wtforms.validators import InputRequired, Length, NumberRange
from app.models import InStock


class NewInventoryForm(FlaskForm):
    item = StringField('Name of Item',validators=[InputRequired(), Length(max=20)])
    units = IntegerField('No of Units',validators=[InputRequired(), NumberRange(min=1,message='Invalid no of units')])
    description =TextAreaField('Description',validators=[Length(min=5,max=1000)])
    submit = SubmitField('Add Item')

class DisburseInventoryForm(FlaskForm):
    item = SelectField('Name of Item',validators=[InputRequired()])
    units = IntegerField('No of Units',validators=[InputRequired(), NumberRange(min=1,message='Invalid no of units')])
    destination = StringField('Destination',validators=[InputRequired()])
    description = TextAreaField('Description',validators=[Length(min=5,max=1000)])
    submit = SubmitField('Disburse Item')

    # ii
    def __init__(self, *args, **kwargs):
        super(DisburseInventoryForm, self).__init__(*args, **kwargs)
        self.item.choices = [stock.item for stock in InStock.query.all()]

    # validate function that ensures disbursed units in stock
    def validate_units(self, units):
        inv = InStock.query.filter_by(item=self.item.data).first()
        if units.data > inv.units:
            raise ValueError('Not enough units in stock.')
