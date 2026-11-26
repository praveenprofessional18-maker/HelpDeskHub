from flask import Blueprint, abort, flash, g, redirect, render_template, request, url_for

from app.auth import login_required
from app.constants import CATEGORIES, PRIORITIES, STATUS_OPEN
from app.models import Ticket, db


tickets = Blueprint("tickets", __name__)


@tickets.route("/dashboard")
@login_required
def dashboard():
    user_tickets = (
        Ticket.query.filter_by(user_id=g.user.id)
        .order_by(Ticket.created_at.desc())
        .all()
    )
    return render_template("dashboard.html", tickets=user_tickets)


@tickets.route("/tickets/new", methods=("GET", "POST"))
@login_required
def create_ticket():
    values = {"title": "", "category": "", "priority": "", "description": ""}
    errors = {}

    if request.method == "POST":
        values = {
            "title": request.form.get("title", "").strip(),
            "category": request.form.get("category", "").strip(),
            "priority": request.form.get("priority", "").strip(),
            "description": request.form.get("description", "").strip(),
        }

        if not values["title"]:
            errors["title"] = "Enter a ticket title."
        elif len(values["title"]) > 120:
            errors["title"] = "Title must be 120 characters or fewer."

        if values["category"] not in CATEGORIES:
            errors["category"] = "Choose a listed category."

        if values["priority"] not in PRIORITIES:
            errors["priority"] = "Choose a listed priority."

        if not values["description"]:
            errors["description"] = "Describe the issue."
        elif len(values["description"]) > 5000:
            errors["description"] = "Description must be 5,000 characters or fewer."

        if errors:
            return render_template(
                "create_ticket.html",
                values=values,
                errors=errors,
                categories=CATEGORIES,
                priorities=PRIORITIES,
            ), 400

        ticket = Ticket(
            user_id=g.user.id,
            title=values["title"],
            category=values["category"],
            priority=values["priority"],
            description=values["description"],
            status=STATUS_OPEN,
        )
        db.session.add(ticket)
        db.session.commit()
        flash("Your ticket has been submitted.", "success")
        return redirect(url_for("tickets.ticket_detail", ticket_id=ticket.id))

    return render_template(
        "create_ticket.html",
        values=values,
        errors=errors,
        categories=CATEGORIES,
        priorities=PRIORITIES,
    )
