from datetime import datetime, timezone

from flask_sqlalchemy import SQLAlchemy

from app.constants import STATUS_OPEN, USER_ROLE


db = SQLAlchemy()


def utc_now():
    return datetime.now(timezone.utc)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(254), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False, default=USER_ROLE)
    created_at = db.Column(db.DateTime(timezone=True), nullable=False, default=utc_now)

    tickets = db.relationship(
        "Ticket", back_populates="user", cascade="all, delete-orphan"
    )
