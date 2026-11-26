import os

from dotenv import load_dotenv
from flask import Flask, g, render_template, session
from flask_wtf.csrf import CSRFProtect

load_dotenv()

from config import Development, Production, Testing
from app.admin import admin
from app.auth import auth
from app.models import User, db
from app.tickets import tickets

csrf = CSRFProtect()
CONFIGS = {
    "development": Development,
    "testing": Testing,
    "production": Production,
}


def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    config_name = os.environ.get("FLASK_CONFIG", "development").lower()
    if config_name not in CONFIGS:
        raise ValueError(f"Unknown Flask configuration: {config_name}")
    app.config.from_object(CONFIGS[config_name])
    if test_config:
        app.config.update(test_config)
    if not app.config.get("SECRET_KEY"):
        raise RuntimeError("Set SECRET_KEY in your environment or .env file.")

    db.init_app(app)
    csrf.init_app(app)
    app.register_blueprint(auth)
    app.register_blueprint(tickets)
    app.register_blueprint(admin)

    @app.before_request
    def load_logged_in_user():
        user_id = session.get("user_id")
        g.user = db.session.get(User, user_id) if user_id is not None else None
        if user_id is not None and g.user is None:
            session.pop("user_id", None)

    @app.context_processor
    def inject_user():
        return {"current_user": g.get("user")}

    @app.template_filter("ticket_code")
    def ticket_code(ticket_id):
        return f"HD-{ticket_id:04d}"

    @app.get("/")
    def index():
        return render_template("index.html")

    @app.errorhandler(400)
    def bad_request(error):
        return render_template("errors/400.html", error=error), 400

    @app.errorhandler(403)
    def forbidden(error):
        return render_template("errors/403.html", error=error), 403

    @app.errorhandler(404)
    def not_found(error):
        return render_template("errors/404.html", error=error), 404

    @app.errorhandler(500)
    def server_error(error):
        db.session.rollback()
        return render_template("errors/500.html", error=error), 500

    register_commands(app)

    with app.app_context():
        db.create_all()

    return app
