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


class Development(Config):
    DEBUG = True


class Testing(Config):
    TESTING = True
    WTF_CSRF_ENABLED = False


class Production(Config):
    DEBUG = False
    SESSION_COOKIE_SECURE = True

    @classmethod
    def validate(cls):
        secret_key = os.environ.get("SECRET_KEY")

        if not secret_key or secret_key == "replace-this-with-a-long-random-value":
            raise RuntimeError(
                "A strong SECRET_KEY must be configured in production."
            )

        if len(secret_key) < 32:
            raise RuntimeError(
                "Production SECRET_KEY must be at least 32 characters long."
            )