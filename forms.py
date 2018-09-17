
from flask_wtf import FlaskForm
from wtforms import (StringField, PasswordField, BooleanField, 
SubmitField, HiddenField, TextAreaField, TextField, SelectField, RadioField)
from wtforms.validators import DataRequired, InputRequired, NumberRange

# This is just for testing some fields
class AddItemFormTest(FlaskForm):
    catalog = SelectField('test', choices = [('SF','sf'),('SAC', 'sac')])
    test2 = RadioField('test2', choices = [('SF','sf'),('SAC', 'sac')])
    item = TextAreaField('item', validators=[DataRequired()])
    # Gender = RadioField('Gender', choices = [('M','Male'),('F','Female')])
   
    # password = PasswordField('Password', validators=[DataRequired()])
    #remember_me = BooleanField('Remember Me')
    submit = SubmitField('Add Item')


class AddItemForm(FlaskForm):
    item_id = HiddenField('item_id')
    name = TextField('name', validators=[DataRequired()])
    description = TextAreaField('description', validators=[DataRequired()])
    submit = SubmitField('Add/Edit Item')

class AddCatalogForm(FlaskForm):
    item_id = HiddenField('item_id')
    name = TextField('name', validators=[DataRequired()])
    submit = SubmitField('Add/Edit Item')