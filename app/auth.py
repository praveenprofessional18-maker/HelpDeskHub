from functools import wraps
from urllib.parse import urljoin, urlsplit

from flask import (
    Blueprint,
    abort,
    flash,
    g,
    redirect,
    render_template,
    request,
    session,
    url_for,
)
from werkzeug.security import check_password_hash, generate_password_hash

from app.constants import ADMIN_ROLE, USER_ROLE
from app.models import User, db
from app.validation import normalize_email, valid_email


auth = Blueprint("auth", __name__)


def login_required(view):
    @wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for("auth.login", next=request.full_path))
        return view(**kwargs)

    return wrapped_view


def admin_required(view):
    @wraps(view)
    @login_required
    def wrapped_view(**kwargs):
        if g.user.role != ADMIN_ROLE:
            abort(403)
        return view(**kwargs)

    return wrapped_view


def is_safe_next_url(target):
    if not target or not target.startswith("/") or target.startswith("//"):
        return False
    if "\\" in target or any(ord(char) < 32 for char in target):
        return False

    destination = urlsplit(urljoin(request.host_url, target))
    return destination.scheme in {"http", "https"} and destination.netloc == request.host


@auth.route("/register", methods=("GET", "POST"))
def register():
    values = {"name": "", "email": ""}
    errors = {}

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = normalize_email(request.form.get("email", ""))
        password = request.form.get("password", "")
        confirmation = request.form.get("confirm_password", "")
        values = {"name": name, "email": email}

        if not name:
            errors["name"] = "Enter your full name."
        elif len(name) > 100:
            errors["name"] = "Name must be 100 characters or fewer."

        if not email:
            errors["email"] = "Enter your email address."
        elif len(email) > 254 or not valid_email(email):
            errors["email"] = "Enter a valid email address."

        if not password:
            errors["password"] = "Enter a password."
        elif len(password) < 8:
            errors["password"] = "Password must be at least 8 characters."
        elif len(password) > 128:
            errors["password"] = "Password must be 128 characters or fewer."

        if not confirmation:
            errors["confirm_password"] = "Confirm your password."
        elif len(confirmation) < 8:
            errors["confirm_password"] = "Password must be at least 8 characters."
        elif len(confirmation) > 128:
            errors["confirm_password"] = "Password must be 128 characters or fewer."
        elif password != confirmation:
            errors["confirm_password"] = "Passwords do not match."

        if email and valid_email(email) and User.query.filter_by(email=email).first():
            errors["email"] = "An account with that email already exists."

        if errors:
            return render_template("register.html", values=values, errors=errors), 400

        user = User(
            name=name,
            email=email,
            password_hash=generate_password_hash(password),
            role=USER_ROLE,
        )
        db.session.add(user)
        db.session.commit()
        flash("Your account is ready. You can now log in.", "success")
        return redirect(url_for("auth.login"))

    return render_template("register.html", values=values, errors=errors)


@auth.route("/login", methods=("GET", "POST"))
def login():
    if request.method == "POST":
        email = normalize_email(request.form.get("email", ""))
        password = request.form.get("password", "")
        user = None

        if len(email) <= 254 and valid_email(email) and 8 <= len(password) <= 128:
            user = User.query.filter_by(email=email).first()

        if user is None or not check_password_hash(user.password_hash, password):
            flash("Invalid email or password", "error")
            return render_template(
                "login.html",
                email=email,
                next_url=request.form.get("next", ""),
            ), 401

        session.clear()
        session["user_id"] = user.id
        destination = request.form.get("next", "")
        if is_safe_next_url(destination):
            return redirect(destination)
        return redirect(url_for("tickets.dashboard"))

    return render_template(
        "login.html",
        email="",
        next_url=request.args.get("next", ""),
    )


@auth.post("/logout")
@login_required
def logout():
    session.clear()
    flash("You have been logged out.", "success")
    return redirect(url_for("index"))
