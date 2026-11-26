import pytest

from app import create_app, get_config_class
from config import Development, Production, Testing


def test_get_config_class_normalizes_supported_names():
    name, config_class = get_config_class("  PRODUCTION  ")

    assert name == "production"
    assert config_class is Production


@pytest.mark.parametrize(
    ("name", "config_class"),
    (
        ("development", Development),
        ("testing", Testing),
        ("production", Production),
    ),
)
def test_get_config_class_resolves_supported_names(name, config_class):
    assert get_config_class(name) == (name, config_class)


def test_get_config_class_reports_supported_names_for_unknown_config():
    with pytest.raises(RuntimeError, match="development, production, testing"):
        get_config_class("staging")


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
