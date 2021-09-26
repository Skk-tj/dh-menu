from sqlalchemy.dialects import postgresql

from app import db


class MessageOfTheDay(db.Model):
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
