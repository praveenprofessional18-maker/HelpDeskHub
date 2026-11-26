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


def get_config_class(config_name):
    normalized_name = str(config_name).strip().lower()
    if normalized_name not in CONFIGS:
        supported = ", ".join(sorted(CONFIGS))
        raise RuntimeError(
            f"Unknown Flask configuration '{config_name}'. "
            f"Expected one of: {supported}."
        )
    return normalized_name, CONFIGS[normalized_name]


def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    config_name, config_class = get_config_class(
        os.environ.get("FLASK_CONFIG", "development")
    )
    app.config.from_object(config_class)
    if test_config:
        app.config.update(test_config)
    if not app.config.get("TESTING"):
        config_class.validate(app.config)

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


def register_commands(app):
    import click
    from datetime import timedelta

    from werkzeug.security import generate_password_hash

    from app.constants import (
        ADMIN_ROLE,
        CATEGORY_ACCOUNT,
        CATEGORY_SOFTWARE,
        CATEGORY_WIFI,
        PRIORITY_HIGH,
        PRIORITY_LOW,
        PRIORITY_MEDIUM,
        STATUS_IN_PROGRESS,
        STATUS_OPEN,
        STATUS_RESOLVED,
        USER_ROLE,
    )
    from app.models import Ticket, User, utc_now
    from app.validation import normalize_email, valid_email

    @app.cli.command("create-admin")
    def create_admin():
        """Create an administrator account interactively."""
        name = click.prompt("Admin full name").strip()
        email = normalize_email(click.prompt("Admin email"))
        password = click.prompt(
            "Admin password (minimum 8 characters)",
            hide_input=True,
            confirmation_prompt=True,
        )

        if not name or len(name) > 100:
            raise click.ClickException("Name is required and must be 100 characters or fewer.")
        if len(email) > 254 or not valid_email(email):
            raise click.ClickException("Enter a valid email address.")
        if len(password) < 8 or len(password) > 128:
            raise click.ClickException("Password must be between 8 and 128 characters.")
        if User.query.filter_by(email=email).first():
            raise click.ClickException("An account with that email already exists.")

        user = User(
            name=name,
            email=email,
            password_hash=generate_password_hash(password),
            role=ADMIN_ROLE,
        )
        db.session.add(user)
        db.session.commit()
        click.echo(f"Administrator account created for {email}.")

    @app.cli.command("seed-demo")
    def seed_demo():
        """Create demo user/admin accounts and example tickets."""
        demo_user_email = "student@college.edu"
        demo_admin_email = "admin@college.edu"
        demo_user = User.query.filter_by(email=demo_user_email).first()
        demo_admin = User.query.filter_by(email=demo_admin_email).first()

        if demo_user and demo_user.role != USER_ROLE:
            raise click.ClickException("The demo student email is already used by an admin.")
        if demo_admin and demo_admin.role != ADMIN_ROLE:
            raise click.ClickException("The demo admin email is already used by a user.")

        user_password = None
        admin_password = None
        if demo_user is None:
            user_password = click.prompt(
                "Demo student password (minimum 8 characters)",
                hide_input=True,
                confirmation_prompt=True,
            )
        if demo_admin is None:
            admin_password = click.prompt(
                "Demo admin password (minimum 8 characters)",
                hide_input=True,
                confirmation_prompt=True,
            )
        for password in (user_password, admin_password):
            if password is not None and (len(password) < 8 or len(password) > 128):
                raise click.ClickException("Passwords must be between 8 and 128 characters.")

        if demo_user is None:
            demo_user = User(
                name="Alex Morgan",
                email=demo_user_email,
                password_hash=generate_password_hash(user_password),
                role=USER_ROLE,
            )
            db.session.add(demo_user)
        if demo_admin is None:
            demo_admin = User(
                name="IT Administrator",
                email=demo_admin_email,
                password_hash=generate_password_hash(admin_password),
                role=ADMIN_ROLE,
            )
            db.session.add(demo_admin)
        db.session.flush()

        samples = (
            ("Wi-Fi disconnects in the science building", CATEGORY_WIFI, PRIORITY_MEDIUM,
             "My laptop disconnects from campus Wi-Fi every few minutes in room S214.",
             STATUS_IN_PROGRESS, 1),
            ("Unable to install the statistics software", CATEGORY_SOFTWARE, PRIORITY_LOW,
             "The installer stops before finishing on a college lab computer.",
             STATUS_OPEN, 2),
            ("Reset access to student portal", CATEGORY_ACCOUNT, PRIORITY_HIGH,
             "I cannot access the student portal after changing my password.",
             STATUS_RESOLVED, 3),
        )
        now = utc_now()
        for title, category, priority, description, status, days_ago in samples:
            existing = Ticket.query.filter_by(user_id=demo_user.id, title=title).first()
            if existing is None:
                created_at = now - timedelta(days=days_ago)
                db.session.add(Ticket(
                    user_id=demo_user.id,
                    title=title,
                    category=category,
                    priority=priority,
                    description=description,
                    status=status,
                    created_at=created_at,
                    updated_at=created_at,
                ))

        db.session.commit()
        click.echo("Demo data is ready. Sign in with student@college.edu or admin@college.edu.")
