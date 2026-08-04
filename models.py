from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()


class Record(db.Model):
    __tablename__ = "records"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    name = db.Column(
        db.String(100),
        nullable=False
    )

    email = db.Column(
        db.String(120),
        unique=True,
        nullable=False
    )

    phone = db.Column(
        db.String(10),
        unique=True,
        nullable=False
    )

    department = db.Column(
        db.String(100),
        nullable=False
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

    # ---- AI Duplicate Assistant fields ----

    is_duplicate = db.Column(
        db.Boolean,
        default=False,
        nullable=False
    )

    similarity_score = db.Column(
        db.Integer,
        nullable=True
    )

    duplicate_of_id = db.Column(
        db.Integer,
        db.ForeignKey("records.id"),
        nullable=True
    )

    duplicate_of = db.relationship(
        "Record",
        remote_side=[id],
        foreign_keys=[duplicate_of_id]
    )

    def __repr__(self):
        return f"<Cadet {self.name}>"