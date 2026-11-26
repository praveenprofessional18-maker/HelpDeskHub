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
