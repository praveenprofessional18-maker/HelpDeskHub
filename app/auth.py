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
