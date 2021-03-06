from sqlalchemy.dialects import postgresql
from flask_login import UserMixin

from app import db


class User(db.Model, UserMixin):
    __tablename__ = "user"

    user_id = db.Column(postgresql.TEXT, primary_key=True, nullable=False)
    password_hash = db.Column(postgresql.TEXT, nullable=False)

    def __init__(self, user_id, password_hash):
        self.user_id = user_id
        self.password_hash = password_hash

    def get_id(self):
        return self.user_id
