from flask_wtf import FlaskForm
from wtforms import SubmitField, TextAreaField, StringField
from wtforms.fields.html5 import DateField
from wtforms.validators import DataRequired


class MessageOfTheDayForm(FlaskForm):
    date = DateField("Date", validators=[DataRequired("This field is required. ")])
    message_title = StringField("Message Title", validators=[DataRequired("This field is required. ")])
    message_description = TextAreaField("Message Detail", validators=[DataRequired("This field is required. ")])

    submit = SubmitField('Submit')
