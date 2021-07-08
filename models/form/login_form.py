from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired


class LoginForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired("This field is required. ")])
    password = PasswordField("Password", validators=[DataRequired("This field is required. ")])

    submit = SubmitField('Login')
