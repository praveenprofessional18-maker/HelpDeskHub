import os


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY")
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL", "sqlite:///helpdeskhub.db"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    WTF_CSRF_ENABLED = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    ENVIRONMENT = "base"

    @classmethod
    def validate(cls, app_config=None):
        app_config = app_config or {}
        secret_key = app_config.get("SECRET_KEY", cls.SECRET_KEY)
        if not secret_key or secret_key == "replace-this-with-a-long-random-value":
            raise RuntimeError(
                "A strong SECRET_KEY must be configured before the app starts."
            )
        if len(secret_key) < 32:
            raise RuntimeError(
                "SECRET_KEY must be at least 32 characters long."
            )


class Development(Config):
    DEBUG = True
    ENVIRONMENT = "development"


class Testing(Config):
    TESTING = True
    WTF_CSRF_ENABLED = False
    ENVIRONMENT = "testing"


class Production(Config):
    DEBUG = False
    SESSION_COOKIE_SECURE = True
    ENVIRONMENT = "production"

    @classmethod
    def validate(cls, app_config=None):
        super().validate(app_config)