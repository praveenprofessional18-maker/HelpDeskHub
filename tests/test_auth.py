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
