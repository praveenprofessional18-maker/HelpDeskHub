# HelpDeskHub

HelpDeskHub is a full-stack IT support ticket management system built with Flask and SQLite. Users can register, submit technical issues, track ticket status, and view their own ticket history. Administrators can monitor dashboard statistics, manage all tickets, update status, and view registered users.

## Features

- Session-based registration and login with Werkzeug password hashing
- Server-side CSRF protection and role-based access control
- User ticket creation, search, filtering, and ownership checks
- Admin dashboard, ticket management, status updates, and user directory
- Responsive dark SaaS interface with animated states and toast notifications
- SQLite database using Flask-SQLAlchemy

## Technology Stack

- Python and Flask
- Flask-SQLAlchemy and SQLite
- Flask-WTF CSRF protection
- HTML5, CSS3, and vanilla JavaScript

## Project Structure

```text
HelpDeskHub/
├── frontend/
│   ├── pages/
│   ├── css/
│   ├── js/
│   ├── images/
│   └── assets/
├── backend/
│   ├── app/
│   ├── tests/
│   ├── config/
│   ├── instance/
│   ├── requirements.txt
│   └── run.py
├── docs/
├── .gitignore
└── README.md
```

## Database

The application uses SQLite and creates `instance/helpdeskhub.db` automatically. The database contains `users` and `tickets` tables. Public registration always assigns the `user` role; the role is never read from submitted form data.

## Installation

Windows PowerShell:

```powershell
cd HelpDeskHub
py -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r backend\requirements.txt
Copy-Item backend\.env.example .env
python backend\run.py
```

Open `http://127.0.0.1:5000`.

Set `SECRET_KEY` in `.env` to a secure random value for non-development use:

```powershell
python -c "import secrets; print(secrets.token_hex(32))"
```

## Create an Admin

No public registration path creates administrators. For local setup, use the Flask shell:

```powershell
python -c "from app import create_app,db; from app.models import User; a=create_app(); c=a.app_context(); c.push(); u=User.query.filter_by(email='admin@example.com').first(); u.role='admin' if u else None; db.session.commit() if u else None"
```

Register the account first, then run the command above.

## Testing

```powershell
python -m pytest backend\tests -q
```

The test suite covers registration, login, ticket ownership and creation, admin authorization, and status updates.

## GitHub Readiness

- Never commit `.env`, the virtual environment, or database files
- Change the secret key before deployment
- Use HTTPS and secure session cookies in production

## Future Enhancements

- Email notifications
- Ticket comments and attachments
- Password reset
- Pagination and audit history
- PostgreSQL or MySQL deployment
