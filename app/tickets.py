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
