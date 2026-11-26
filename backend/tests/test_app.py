import pytest

from app import create_app, db
from app.models import Ticket, User


@pytest.fixture
def app():
    app = create_app({
        "TESTING": True,
        "WTF_CSRF_ENABLED": False,
        "SECRET_KEY": "test-secret",
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
    })
    with app.app_context():
        db.drop_all()
        db.create_all()
    yield app
    with app.app_context():
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


def register(client, name="Alex Morgan", email="alex@example.com", password="Password123"):
    return client.post("/register", data={
        "name": name,
        "email": email,
        "password": password,
        "confirm_password": password,
    }, follow_redirects=True)


def login(client, email="alex@example.com", password="Password123"):
    return client.post("/login", data={"email": email, "password": password}, follow_redirects=True)


def test_registration_login_logout_and_duplicate(client, app):
    response = register(client)
    assert response.status_code == 200
    assert b"Account created successfully" in response.data

    with app.app_context():
        user = User.query.filter_by(email="alex@example.com").one()
        assert user.role == "user"
        assert user.password_hash != "Password123"

    assert register(client).status_code == 200
    assert b"already exists" in client.post("/register", data={
        "name": "Alex",
        "email": "alex@example.com",
        "password": "Password123",
        "confirm_password": "Password123",
    }, follow_redirects=True).data

    assert b"Welcome" in login(client).data
    assert client.post("/logout", follow_redirects=True).status_code == 200


def test_ticket_create_list_detail_and_ownership(client, app):
    register(client, email="one@example.com")
    login(client, email="one@example.com")
    response = client.post("/tickets/new", data={
        "title": "Office Wi-Fi is disconnected",
        "category": "Network / Wi-Fi",
        "priority": "High",
        "description": "The office Wi-Fi drops every few minutes.",
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b"HDH-00001" in response.data

    with app.app_context():
        ticket = Ticket.query.one()
        ticket_id = ticket.id
    assert client.get("/tickets").status_code == 200
    assert client.get(f"/tickets/{ticket_id}").status_code == 200

    register(client, name="Sam Lee", email="two@example.com")
    login(client, email="two@example.com")
    assert client.get(f"/tickets/{ticket_id}").status_code == 403


def test_admin_status_update_and_user_route_authorization(client, app):
    register(client)
    login(client)
    client.post("/tickets/new", data={
        "title": "Printer is not working",
        "category": "Hardware",
        "priority": "Medium",
        "description": "The office printer is not responding.",
    })

    assert client.get("/admin").status_code == 403

    with app.app_context():
        user = User.query.filter_by(email="alex@example.com").one()
        user.role = "admin"
        ticket = Ticket.query.one()
        ticket_id = ticket.id
        db.session.commit()

    assert client.get("/admin").status_code == 200
    assert client.get("/admin/users").status_code == 200
    response = client.post(f"/admin/tickets/{ticket_id}/status", data={
        "status": "Resolved",
    }, follow_redirects=True)
    assert response.status_code == 200
    with app.app_context():
        assert db.session.get(Ticket, ticket_id).status == "Resolved"
