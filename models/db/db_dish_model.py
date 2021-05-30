from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.dialects import postgresql

import config
from models.db.db_meal_enum import meal_enum_sql
from models.meal_enum import Meal

db = SQLAlchemy()


class Dish(db.Model):
    __table_args__ = {"schema": config.get_config_from_env().DATABASE_SCHEMA}
    __tablename__ = "dish"

    dish_id = db.Column(postgresql.UUID(as_uuid=True), primary_key=True)
    dish_name = db.Column(postgresql.TEXT, unique=True, nullable=False)
    is_vegan = db.Column(postgresql.BOOLEAN, nullable=False)
    is_vegetarian = db.Column(postgresql.BOOLEAN, nullable=False)
    is_halal = db.Column(postgresql.BOOLEAN, nullable=False)
    is_gluten_free = db.Column(postgresql.BOOLEAN, nullable=False)
    annotation = db.Column(postgresql.TEXT)
    for_which_meal = db.Column(meal_enum_sql, nullable=False)

    def __init__(self, dish_id, dish_name, is_vegan, is_vegetarian, is_halal, is_gluten_free, annotation,
                 for_which_meal):
        self.dish_id = dish_id
        self.dish_name = dish_name
        self.is_vegan = is_vegan
        self.is_vegetarian = is_vegetarian
        self.is_halal = is_halal
        self.is_gluten_free = is_gluten_free
        self.annotation = annotation
        self.for_which_meal = for_which_meal

    def to_dict(self):
        return {
            "dish_id": self.dish_id,
            "dish_name": self.dish_name,
            "is_vegan": self.is_vegan,
            "is_vegetarian": self.is_vegetarian,
            "is_halal": self.is_halal,
            "is_gluten_free": self.is_gluten_free,
            "annotation": self.annotation,
            "for_which_meal_int": Meal[self.for_which_meal].value,
            "for_which_meal_str": self.for_which_meal
        }
