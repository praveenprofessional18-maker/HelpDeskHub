from app.models import Ticket, db

from tests.helpers import login


def test_normal_user_cannot_open_admin(client, user):
    login(client)
    response = client.get("/admin")

    assert response.status_code == 403


def test_admin_updates_ticket_status(client, app, admin_user, ticket):
    login(client, email="admin@college.edu")
    response = client.post(
        f"/admin/tickets/{ticket}/status",
        data={"status": "In Progress"},
    )

    assert response.status_code == 302
    with app.app_context():
        saved_ticket = db.session.get(Ticket, ticket)
        assert saved_ticket.status == "In Progress"
