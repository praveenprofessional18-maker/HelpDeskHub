import os
from pathlib import Path
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import CSRFProtect
from dotenv import load_dotenv


db = SQLAlchemy()
csrf = CSRFProtect()
ROOT_DIR = Path(__file__).resolve().parents[2]
FRONTEND_DIR = ROOT_DIR / "frontend"


def create_app(test_config=None):
    load_dotenv(ROOT_DIR / ".env")
    app = Flask(
        __name__,
        template_folder=str(FRONTEND_DIR / "pages"),
        static_folder=str(FRONTEND_DIR),
        static_url_path="/static",
    )
    app.config.from_object("config.Config")

    if test_config:
        app.config.update(test_config)
    if not app.config.get("SECRET_KEY"):
        app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "development-only-change-me")

    db.init_app(app)
    csrf.init_app(app)

    from .models import User, Ticket
    from .auth import auth_bp
    from .tickets import tickets_bp
    from .admin import admin_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(tickets_bp)
    app.register_blueprint(admin_bp)

    with app.app_context():
        db.create_all()

    return app

