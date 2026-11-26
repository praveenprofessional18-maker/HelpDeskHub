# HelpDeskHub

HelpDeskHub is a small Flask and SQLite college IT help-desk project. It includes account registration and login, user-owned tickets, and an admin ticket queue.

## Requirements

- Python 3.10 or newer
- PowerShell on Windows (or a terminal with equivalent commands)

## Install

From the project folder, create and activate a virtual environment:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Install the project dependencies:

```powershell
python -m pip install -r requirements.txt
```

## Configure the app

Copy the example environment file and generate a private key:

```powershell
Copy-Item .env.example .env
python -c "import secrets; print(secrets.token_hex(32))"
```

Open `.env` and set `SECRET_KEY` to the generated value. Keep `.env` private and do not commit it. The SQLite database is created automatically on startup at the configured `DATABASE_URL`.

Supported Flask configuration names are `development`, `testing`, and `production`. The application rejects unknown names with a startup error that lists the supported options.

The app uses the development configuration by default. To choose another `config.py` class, set `FLASK_CONFIG=production` or `FLASK_CONFIG=testing` in the environment.

Non-testing configurations validate the configured `SECRET_KEY` during startup. The key must be at least 32 characters and must not use the placeholder value from `.env.example`. Production configuration also enables secure session cookies.

## Create an admin account

Run the interactive command and enter an admin name, email and password when prompted:

```powershell
flask --app run.py create-admin
```

To create sample accounts and tickets for a demo instead:

```powershell
flask --app run.py seed-demo
```

The demo command prompts for student and admin passwords if those accounts do not already exist. It does not print or store the plain-text passwords.

## Run the app

```powershell
flask --app run.py run
```

Open `http://127.0.0.1:5000` in a browser. Registration creates a normal user account; admin privileges are only available through the CLI commands.

## Run the tests

```powershell
python -m pytest
```

The tests use an in-memory SQLite database and disable CSRF for test requests. A separate test checks that a POST without a CSRF token is rejected.

## Manual test checklist

- Register using a valid email; try a duplicate email and mismatched or short passwords.
- Log in with a wrong password and confirm the message stays generic.
- Create a ticket, then view it in the dashboard and detail page.
- Log out and confirm the dashboard requires login.
- Sign in as an admin, filter/search the queue and change a ticket status one step at a time.
- Try to open another user's ticket while signed in as a normal user; it should return 404.
- Check the pages at mobile and desktop widths and use the keyboard to navigate forms.
