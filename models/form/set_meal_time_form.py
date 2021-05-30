from flask_wtf import FlaskForm
from wtforms import SelectField, SubmitField, BooleanField
from wtforms.fields.html5 import TimeField
from wtforms.validators import DataRequired

from models.meal_enum import Meal


class SetMealTimeForm(FlaskForm):
    meal = SelectField("Select meal",
                       choices=[(int(Meal.Breakfast), "Breakfast"), (int(Meal.Lunch), "Lunch"),
                                (int(Meal.Dinner), "Dinner")],
                       validators=[DataRequired("This field is required. ")])
    meal_start = TimeField("", validators=[DataRequired("This field is required. ")])
    meal_end = TimeField("", validators=[DataRequired("This field is required. ")])
    is_work_day = BooleanField("Monday to Friday Time?")

    submit = SubmitField("Confirm")
