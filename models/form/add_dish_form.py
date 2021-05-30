from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, BooleanField, SubmitField, SelectField
from wtforms.validators import DataRequired

from models.meal_enum import Meal


class AddDishForm(FlaskForm):
    uuid = None
    dish_name = StringField("Dish Name", validators=[DataRequired("This field is required. ")])
    annotation = TextAreaField("Annotation For This Dish")
    is_vegan = BooleanField("Is this dish Vegan?")
    is_vegetarian = BooleanField("Is this dish Vegetarian?")
    is_halal = BooleanField("Is this dish Halal?")
    is_gluten_free = BooleanField("Is this dish Gluten Free?")
    for_which_meal = SelectField("Which meal is this dish for?",
                                 choices=[(int(Meal.Breakfast), "Breakfast"), (int(Meal.Lunch), "Lunch"),
                                          (int(Meal.Dinner), "Dinner")],
                                 validators=[DataRequired("This field is required. ")])
    submit = SubmitField('Add')
