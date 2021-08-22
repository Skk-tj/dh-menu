from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.dialects import postgresql

import config

db = SQLAlchemy()


class MessageOfTheDay(db.Model):
    __table_args__ = {"schema": config.get_config_from_env().DATABASE_SCHEMA}
    __tablename__ = "message_of_the_day"

    id = db.Column(postgresql.UUID, primary_key=True)
    date = db.Column(postgresql.DATE, nullable=False)
    message_title = db.Column(postgresql.TEXT, nullable=False)
    message_description = db.Column(postgresql.TEXT, nullable=False)

    def __init__(self, message_id, date, message_title, message_description):
        self.id = message_id
        self.date = date
        self.message_title = message_title
        self.message_description = message_description
