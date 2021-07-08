from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, EqualTo, Length, Regexp


class RegisterForm(FlaskForm):
    username = StringField("Username", validators=[
        Length(min=4, message="Username must have more than 4 characters. "),
        DataRequired("This field is required. "),
        Regexp('^\w+$', message="Username must contain only alpha-numerical characters or underscores. ")
    ])
    password = PasswordField("Password", validators=[
        Length(min=8, message="Password must have more than 8 characters. "),
        DataRequired("This field is required. "),
        EqualTo('confirm', message='Passwords must match. ')
    ])
    confirm = PasswordField("Confirm Password", validators=[
        EqualTo('password', message='Passwords must match. '),
        DataRequired("This field is required. ")
    ])

    submit = SubmitField('Register')
