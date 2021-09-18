from sqlalchemy.dialects import postgresql

import config
from app import db


class DaysPublished(db.Model):
    __table_args__ = {"schema": config.get_config_from_env().DATABASE_SCHEMA}
    __tablename__ = "days_published"

    date = db.Column(postgresql.DATE, primary_key=True)
    is_published = db.Column(postgresql.BOOLEAN, nullable=False)

    def __init__(self, date, is_published):
        self.date = date
        self.is_published = is_published
