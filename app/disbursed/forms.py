from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField, IntegerField, SelectField
from wtforms.validators import InputRequired, Length, NumberRange
from app.models import InStock

class DisburseInventoryForm(FlaskForm):
    item = SelectField('Name of Item',validators=[InputRequired()])
    units = IntegerField('No of Units',validators=[InputRequired(), NumberRange(min=1,message='Invalid no of units')])
    destination = StringField('Destination',validators=[InputRequired()])
    description = TextAreaField('Description',validators=[Length(max=1000)])
    submit = SubmitField('Disburse Item')

    # initialize item field choices with units currently in stock
    def __init__(self, *args, **kwargs):
        super(DisburseInventoryForm, self).__init__(*args, **kwargs)
        self.item.choices = [stock.item for stock in InStock.query.all()]

    # validate function that ensures disbursed units in stock
    def validate_units(self, units):
        inv = InStock.query.filter_by(item=self.item.data).first()
        if units.data > inv.units:
            raise ValueError('Not enough units in stock.')