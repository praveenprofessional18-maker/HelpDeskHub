import pytest

from app import create_app


def test_development_configuration_requires_a_strong_secret(monkeypatch):
    monkeypatch.setenv("FLASK_CONFIG", "development")

    with pytest.raises(RuntimeError, match="at least 32 characters"):
        create_app({
            "TESTING": False,
            "SECRET_KEY": "too-short",
            "SQLALCHEMY_DATABASE_URI": "sqlite://",
        })


def test_production_configuration_enables_secure_cookies(monkeypatch):
    monkeypatch.setenv("FLASK_CONFIG", "production")

    application = create_app({
        "TESTING": False,
        "SECRET_KEY": "s" * 32,
        "SQLALCHEMY_DATABASE_URI": "sqlite://",
    })

    assert application.config["SESSION_COOKIE_SECURE"] is True


def test_testing_configuration_skips_startup_secret_validation():
    application = create_app({
        "TESTING": True,
        "WTF_CSRF_ENABLED": False,
        "SECRET_KEY": "test-secret",
        "SQLALCHEMY_DATABASE_URI": "sqlite://",
    })

    assert application.config["TESTING"] is True
