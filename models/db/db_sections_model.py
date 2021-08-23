from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.dialects import postgresql
from models.db.db_meal_enum import meal_enum_sql

import config

db = SQLAlchemy()


class Sections(db.Model):
    __table_args__ = {"schema": config.get_config_from_env().DATABASE_SCHEMA}
    __tablename__ = "sections"

    section_id = db.Column(postgresql.UUID(as_uuid=True), primary_key=True)
    section_name = db.Column(postgresql.TEXT, nullable=False)
    section_for_which_meal = db.Column(meal_enum_sql, nullable=False)

    def __init__(self, section_id, section_name, section_for_which_meal):
        self.section_id = section_id
        self.section_name = section_name
        self.section_for_which_meal = section_for_which_meal

    def __hash__(self):
        return hash(self.section_id)

    def __eq__(self, other):
        return self.section_id == other.section_id
