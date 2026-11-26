from flask import Blueprint, abort, flash, redirect, render_template, request, url_for
from sqlalchemy import String, cast, or_
from . import db
from .auth import login_required, current_user
from .models import Ticket


tickets_bp = Blueprint("tickets", __name__)
CATEGORIES = ["Network / Wi-Fi", "Hardware", "Software", "Account Access", "Other"]
PRIORITIES = ["Low", "Medium", "High"]


@tickets_bp.route("/dashboard")
@login_required
def dashboard():
    user = current_user()
    if not user:
        abort(401)

    tickets = Ticket.query.filter_by(user_id=user.id).order_by(Ticket.created_at.desc()).all()
    counts = {
        "total": len(tickets),
        "open": sum(t.status == "Open" for t in tickets),
        "progress": sum(t.status == "In Progress" for t in tickets),
        "resolved": sum(t.status == "Resolved" for t in tickets),
    }
    return render_template("dashboard.html", tickets=tickets[:5], counts=counts)


@tickets_bp.route("/tickets/new", methods=["GET", "POST"])
@login_required
def create_ticket():
    user = current_user()
    if request.method == "POST":
        title = request.form.get("title", "").strip()
        category = request.form.get("category", "")
        priority = request.form.get("priority", "")
        description = request.form.get("description", "").strip()

        if len(title) < 5:
            flash("Issue title must be at least 5 characters.", "danger")
        elif category not in CATEGORIES:
            flash("Select a valid issue category.", "danger")
        elif priority not in PRIORITIES:
            flash("Select a valid priority.", "danger")
        elif len(description) < 10:
            flash("Description must be at least 10 characters.", "danger")
        else:
            ticket = Ticket(
                user_id=user.id,
                title=title,
                category=category,
                priority=priority,
                description=description,
                status="Open",
            )
            db.session.add(ticket)
            db.session.commit()
            flash(f"Ticket HDH-{ticket.id:05d} has been created.", "success")
            return redirect(url_for("tickets.ticket_detail", ticket_id=ticket.id))

    return render_template("create_ticket.html", categories=CATEGORIES, priorities=PRIORITIES)


@tickets_bp.route("/tickets")
@login_required
def tickets():
    user = current_user()
    search = request.args.get("q", "").strip()
    status = request.args.get("status", "")
    category = request.args.get("category", "")

    query = Ticket.query.filter_by(user_id=user.id)
    if search:
        pattern = f"%{search}%"
        query = query.filter(or_(Ticket.title.ilike(pattern),
                                 cast(Ticket.id, String).ilike(pattern)))
    if status in {"Open", "In Progress", "Resolved"}:
        query = query.filter_by(status=status)
    if category in CATEGORIES:
        query = query.filter_by(category=category)

    items = query.order_by(Ticket.created_at.desc()).all()
    return render_template("tickets.html", tickets=items, categories=CATEGORIES,
                           selected_status=status, selected_category=category, search=search)


@tickets_bp.route("/tickets/<int:ticket_id>")
@login_required
def ticket_detail(ticket_id):
    user = current_user()
    ticket = db.session.get(Ticket, ticket_id)
    if not ticket:
        abort(404)
    if ticket.user_id != user.id and user.role != "admin":
        abort(403)
    return render_template("ticket_detail.html", ticket=ticket)
