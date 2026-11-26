from sqlalchemy import func, or_

from flask import Blueprint, abort, flash, redirect, render_template, request, url_for

from app.auth import admin_required
from app.constants import CATEGORIES, PRIORITIES, STATUSES, STATUS_TRANSITIONS
from app.models import Ticket, db


admin = Blueprint("admin", __name__)


@admin.get("/admin")
@admin_required
def dashboard():
    status = request.args.get("status", "").strip()
    category = request.args.get("category", "").strip()
    priority = request.args.get("priority", "").strip()
    search = request.args.get("search", "").strip()

    if status and status not in STATUSES:
        abort(400, description="Choose a valid ticket status.")
    if category and category not in CATEGORIES:
        abort(400, description="Choose a valid ticket category.")
    if priority and priority not in PRIORITIES:
        abort(400, description="Choose a valid ticket priority.")
    if len(search) > 120:
        abort(400, description="Search must be 120 characters or fewer.")

    counts = {
        value: db.session.query(func.count(Ticket.id))
        .filter_by(status=value)
        .scalar()
        for value in STATUSES
    }

    query = Ticket.query
    if status:
        query = query.filter_by(status=status)
    if category:
        query = query.filter_by(category=category)
    if priority:
        query = query.filter_by(priority=priority)
    if search:
        search_id = search[3:] if search.upper().startswith("HD-") else search
        match = Ticket.title.ilike(f"%{search}%")
        if search_id.isdigit():
            match = or_(match, Ticket.id == int(search_id))
        query = query.filter(match)

    all_tickets = query.order_by(Ticket.created_at.desc()).all()
    return render_template(
        "admin_dashboard.html",
        tickets=all_tickets,
        counts=counts,
        statuses=STATUSES,
        categories=CATEGORIES,
        priorities=PRIORITIES,
        transitions=STATUS_TRANSITIONS,
        filters={"status": status, "category": category, "priority": priority, "search": search},
    )


@admin.post("/admin/tickets/<int:ticket_id>/status")
@admin_required
def update_status(ticket_id):
    ticket = db.session.get(Ticket, ticket_id)
    if ticket is None:
        abort(404)

    new_status = request.form.get("status", "").strip()
    if new_status not in STATUSES:
        abort(400, description="Choose a valid ticket status.")

    if new_status != ticket.status and new_status != STATUS_TRANSITIONS[ticket.status]:
        abort(400, description="That status transition is not allowed.")

    if new_status != ticket.status:
        ticket.status = new_status
        db.session.commit()
        flash("Ticket status updated.", "success")

    return redirect(url_for("admin.dashboard"))
