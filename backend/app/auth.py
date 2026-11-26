from functools import wraps
from flask import Blueprint, flash, redirect, render_template, request, session, url_for, abort
from email_validator import EmailNotValidError, validate_email
from . import db
from .models import User


auth_bp = Blueprint("auth", __name__)


def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if "user_id" not in session:
            flash("Please log in to continue.", "warning")
            return redirect(url_for("auth.login", next=request.path))
        return view(*args, **kwargs)
    return wrapped


def admin_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if "user_id" not in session:
            flash("Please log in to continue.", "warning")
            return redirect(url_for("auth.login", next=request.path))
        user = db.session.get(User, session["user_id"])
        if not user or user.role != "admin":
            abort(403)
        return view(*args, **kwargs)
    return wrapped


def current_user():
    if "user_id" not in session:
        return None
    return db.session.get(User, session["user_id"])


@auth_bp.app_context_processor
def inject_current_user():
    return {"current_user": current_user()}


@auth_bp.route("/")
def index():
    if "user_id" in session:
        user = current_user()
        if user and user.role == "admin":
            return redirect(url_for("admin.dashboard"))
        return redirect(url_for("tickets.dashboard"))
    return render_template("index.html")


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        confirm = request.form.get("confirm_password", "")

        if len(name) < 2:
            flash("Full name must be at least 2 characters.", "danger")
        elif not email:
            flash("Email address is required.", "danger")
        else:
            try:
                email = validate_email(email, check_deliverability=False).normalized
            except EmailNotValidError:
                flash("Enter a valid email address.", "danger")
                return render_template("register.html")

            if len(password) < 8:
                flash("Password must be at least 8 characters.", "danger")
            elif password != confirm:
                flash("Passwords do not match.", "danger")
            elif User.query.filter_by(email=email).first():
                flash("An account with this email already exists.", "danger")
            else:
                user = User(name=name, email=email, role="user")
                user.set_password(password)
                db.session.add(user)
                db.session.commit()
                flash("Account created successfully. Please log in.", "success")
                return redirect(url_for("auth.login"))

    return render_template("register.html")


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        user = User.query.filter_by(email=email).first()
        if not user or not user.check_password(password):
            flash("Invalid email or password.", "danger")
        else:
            session.clear()
            session["user_id"] = user.id
            session.permanent = True
            flash("Welcome back!", "success")
            if user.role == "admin":
                return redirect(url_for("admin.dashboard"))
            return redirect(url_for("tickets.dashboard"))
    return render_template("login.html")


@auth_bp.post("/logout")
@login_required
def logout():
    session.clear()
    flash("You have been logged out.", "success")
    return redirect(url_for("auth.index"))


@auth_bp.route("/profile")
@login_required
def profile():
    return render_template("profile.html")
