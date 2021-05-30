from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.dialects import postgresql
from models.db.db_meal_enum import meal_enum_sql

from models.db.db_sections_model import Sections
from models.db.db_dish_model import Dish

import config

db = SQLAlchemy()


class MenuForMeal(db.Model):
    __table_args__ = {"schema": config.get_config_from_env().DATABASE_SCHEMA}
    __tablename__ = "menu_for_meal"

    id = db.Column(postgresql.UUID(as_uuid=True), primary_key=True)
    date = db.Column(postgresql.DATE, nullable=False)
    for_which_meal = db.Column(meal_enum_sql, nullable=False)
    section_id = db.Column(postgresql.UUID(as_uuid=True), db.ForeignKey(Sections.section_id), nullable=False)
    dish_id = db.Column(postgresql.UUID(as_uuid=True), db.ForeignKey(Dish.dish_id), nullable=False)

    def __init__(self, id, date, for_which_meal, section_id, dish_id):
        self.id = id
        self.date = date
        self.for_which_meal = for_which_meal
        self.section_id = section_id
        self.dish_id = dish_id
