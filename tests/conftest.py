import secrets

import pytest
from werkzeug.security import generate_password_hash

from app import create_app
from app.constants import ADMIN_ROLE, USER_ROLE
from app.models import Ticket, User, db


@pytest.fixture
def app():
    application = create_app({
        "TESTING": True,
        "WTF_CSRF_ENABLED": False,
        "SECRET_KEY": secrets.token_hex(32),
        "SQLALCHEMY_DATABASE_URI": "sqlite://",
    })
    with application.app_context():
        db.drop_all()
        db.create_all()
    yield application
    with application.app_context():
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def user(app):
    with app.app_context():
        account = User(
            name="Alex Morgan",
            email="alex@college.edu",
            password_hash=generate_password_hash("correct-horse"),
            role=USER_ROLE,
        )
        db.session.add(account)
        db.session.commit()
        return account.id


@pytest.fixture
def admin_user(app):
    with app.app_context():
        account = User(
            name="IT Admin",
            email="admin@college.edu",
            password_hash=generate_password_hash("correct-horse"),
            role=ADMIN_ROLE,
        )
        db.session.add(account)
        db.session.commit()
        return account.id
