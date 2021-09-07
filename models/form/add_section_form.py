from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField
from wtforms.validators import DataRequired

from models.meal_enum import Meal


class AddSectionForm(FlaskForm):
    section_name = StringField("Section Name", validators=[DataRequired("This field is required. ")])
    for_which_meal = SelectField("Which meal is this section for?",
                                 choices=[(int(Meal.Breakfast), "Breakfast"), (int(Meal.Lunch), "Lunch"),
                                          (int(Meal.Dinner), "Dinner")],
                                 validators=[DataRequired("This field is required. ")])
    submit = SubmitField('Add')
