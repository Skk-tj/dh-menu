from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.dialects import postgresql

import config

db = SQLAlchemy()


class PublishVersion(db.Model):
    __table_args__ = {"schema": config.get_config_from_env().DATABASE_SCHEMA}
    __tablename__ = "publish_version"

    id = db.Column(postgresql.UUID(as_uuid=True), primary_key=True)

    def __init__(self, uuid):
        self.id = uuid
