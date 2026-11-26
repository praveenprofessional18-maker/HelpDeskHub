from flask import Blueprint, abort, flash, redirect, render_template, request, url_for
from sqlalchemy import String, cast, or_
from . import db
from .auth import admin_required
from .models import Ticket, User
from .tickets import CATEGORIES


admin_bp = Blueprint("admin", __name__, url_prefix="/admin")
STATUSES = ["Open", "In Progress", "Resolved"]


@admin_bp.route("")
@admin_required
def dashboard():
    tickets = Ticket.query.order_by(Ticket.created_at.desc()).all()
    counts = {
        "tickets": len(tickets),
        "users": User.query.count(),
        "open": sum(t.status == "Open" for t in tickets),
        "progress": sum(t.status == "In Progress" for t in tickets),
        "resolved": sum(t.status == "Resolved" for t in tickets),
    }
    return render_template("admin_dashboard.html", tickets=tickets[:8], counts=counts)


@admin_bp.route("/tickets")
@admin_required
def tickets():
    search = request.args.get("q", "").strip()
    status = request.args.get("status", "")
    category = request.args.get("category", "")
    priority = request.args.get("priority", "")

    query = Ticket.query
    if search:
        pattern = f"%{search}%"
        query = query.filter(or_(Ticket.title.ilike(pattern),
                                 cast(Ticket.id, String).ilike(pattern)))
    if status in STATUSES:
        query = query.filter_by(status=status)
    if category in CATEGORIES:
        query = query.filter_by(category=category)
    if priority in {"Low", "Medium", "High"}:
        query = query.filter_by(priority=priority)

    items = query.order_by(Ticket.created_at.desc()).all()
    return render_template("admin_dashboard.html", tickets=items, counts=None,
                           categories=CATEGORIES, statuses=STATUSES,
                           selected_status=status, selected_category=category,
                           selected_priority=priority, search=search, admin_list=True)


@admin_bp.post("/tickets/<int:ticket_id>/status")
@admin_required
def update_status(ticket_id):
    ticket = db.session.get(Ticket, ticket_id)
    if not ticket:
        abort(404)
    status = request.form.get("status", "")
    if status not in STATUSES:
        flash("Invalid ticket status.", "danger")
    else:
        ticket.status = status
        db.session.commit()
        flash(f"HDH-{ticket.id:05d} updated to {status}.", "success")
    return redirect(request.referrer or url_for("admin.tickets"))


@admin_bp.route("/users")
@admin_required
def users():
    users = User.query.order_by(User.created_at.desc()).all()
    return render_template("admin_users.html", users=users)
