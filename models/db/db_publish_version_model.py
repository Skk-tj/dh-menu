from sqlalchemy.dialects import postgresql

from app import db


class PublishVersion(db.Model):
    __tablename__ = "publish_version"

    id = db.Column(postgresql.UUID(as_uuid=True), primary_key=True)

    def __init__(self, uuid):
        self.id = uuid
