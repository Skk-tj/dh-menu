from flask_wtf import FlaskForm
from wtforms import SelectField, SubmitField
from wtforms.fields.html5 import DateField
from wtforms.validators import DataRequired

from models.meal_enum import Meal


class BuildMenuSelectForm(FlaskForm):
    date = DateField("Select date for the menu", validators=[DataRequired("This field is required. ")])
    meal = SelectField("Select meal",
                       choices=[(int(Meal.Breakfast), "Breakfast"), (int(Meal.Lunch), "Lunch"),
                                (int(Meal.Dinner), "Dinner")],
                       validators=[DataRequired("This field is required. ")])
    submit = SubmitField("Next")
