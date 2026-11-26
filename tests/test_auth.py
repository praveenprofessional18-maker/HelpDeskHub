from werkzeug.security import check_password_hash

from app.models import User


def test_register_valid_account(client, app):
    response = client.post(
        "/register",
        data={
            "name": "  Casey Student  ",
            "email": " CASEY@COLLEGE.EDU ",
            "password": "securepass8",
            "confirm_password": "securepass8",
        },
        follow_redirects=True,
    )

    assert response.status_code == 200
    assert b"Your account is ready" in response.data
    with app.app_context():
        user = User.query.filter_by(email="casey@college.edu").one()
        assert user.name == "Casey Student"
        assert user.role == "user"
        assert user.password_hash != "securepass8"
        assert check_password_hash(user.password_hash, "securepass8")


def test_register_duplicate_email(client, user):
    response = client.post(
        "/register",
        data={
            "name": "Another Student",
            "email": " ALEX@COLLEGE.EDU ",
            "password": "securepass8",
            "confirm_password": "securepass8",
        },
    )

    assert response.status_code == 400
    assert b"already exists" in response.data


def test_wrong_password_uses_generic_error(client, user):
    response = client.post(
        "/login",
        data={"email": "alex@college.edu", "password": "wrongpass"},
    )

    assert response.status_code == 401
    assert b"Invalid email or password" in response.data
    assert b"email does not exist" not in response.data.lower()


def test_logout_then_dashboard_is_blocked(client, user):
    client.post("/login", data={"email": "alex@college.edu", "password": "correct-horse"})
    logout_response = client.post("/logout")
    response = client.get("/dashboard", follow_redirects=True)

    assert logout_response.status_code == 302
    assert response.status_code == 200
    assert b"Login to HelpDeskHub" in response.data
