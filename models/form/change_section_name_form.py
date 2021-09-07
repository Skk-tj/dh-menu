from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired


class ChangeSectionNameForm(FlaskForm):
    new_name = StringField("New Section Name", validators=[DataRequired("This field is required. ")])
    submit = SubmitField('Submit')
