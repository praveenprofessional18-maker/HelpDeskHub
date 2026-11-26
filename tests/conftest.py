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
