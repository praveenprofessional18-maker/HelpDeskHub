from app.models import Ticket, User, db

from tests.helpers import login


def test_create_ticket_valid(client, app, user):
    login(client)
    response = client.post(
        "/tickets/new",
        data={
            "title": "Laptop cannot join campus Wi-Fi",
            "category": "Wi-Fi",
            "priority": "High",
            "description": "It disconnects every few minutes in room C12.",
            "status": "Resolved",
            "user_id": "9999",
        },
    )

    assert response.status_code == 302
    with app.app_context():
        ticket = Ticket.query.filter_by(title="Laptop cannot join campus Wi-Fi").one()
        assert ticket.user_id == user
        assert ticket.status == "Open"
        assert ticket.category == "Wi-Fi"


def test_create_ticket_missing_title(client, app, user):
    login(client)
    response = client.post(
        "/tickets/new",
        data={
            "title": "   ",
            "category": "Hardware",
            "priority": "Low",
            "description": "The classroom keyboard is not responding.",
        },
    )

    assert response.status_code == 400
    assert b"Enter a ticket title" in response.data
    with app.app_context():
        assert Ticket.query.count() == 0


def test_user_can_open_own_ticket(client, ticket):
    login(client)
    response = client.get(f"/tickets/{ticket}")

    assert response.status_code == 200
    assert b"Campus Wi-Fi disconnects" in response.data


def test_user_cannot_open_another_users_ticket(client, app, ticket):
    from werkzeug.security import generate_password_hash

    with app.app_context():
        other_user = User(
            name="Other Student",
            email="other@college.edu",
            password_hash=generate_password_hash("correct-horse"),
        )
        db.session.add(other_user)
        db.session.commit()
        other_id = other_user.id

    client.post(
        "/login",
        data={"email": "other@college.edu", "password": "correct-horse"},
    )
    response = client.get(f"/tickets/{ticket}")

    assert other_id is not None
    assert response.status_code == 404
