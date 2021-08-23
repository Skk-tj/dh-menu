from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.dialects import postgresql

from models.db.db_meal_enum import meal_enum_sql

import config

db = SQLAlchemy()


class MealTime(db.Model):
    __table_args__ = {"schema": config.get_config_from_env().DATABASE_SCHEMA}
    __tablename__ = "meal_time"

    meal = db.Column(meal_enum_sql, primary_key=True, nullable=False)
    time_open = db.Column(postgresql.TIME(timezone=False), nullable=False)
    time_close = db.Column(postgresql.TIME(timezone=False), nullable=False)
    is_work_day = db.Column(postgresql.BOOLEAN(), primary_key=True, nullable=False)
