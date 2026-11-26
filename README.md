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

The app uses the development configuration by default. To choose another `config.py` class, set `FLASK_CONFIG=production` or `FLASK_CONFIG=testing` in the environment.
