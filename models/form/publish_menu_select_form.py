from flask_wtf import FlaskForm
from wtforms import SubmitField
from wtforms.fields.core import StringField
from wtforms.validators import DataRequired
from wtforms.widgets.html5 import WeekInput


class WeekField(StringField):
    widget = WeekInput()


class PublishMenuSelectForm(FlaskForm):
    week = WeekField("Select week", validators=[DataRequired("This field is required. ")])

    submit = SubmitField("Next")
