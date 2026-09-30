# Student Civic Hub — Persistent Streamlit + Supabase

A clean, student-friendly platform for:
- everyday campus problem reporting
- private student petitions
- verified organizer updates
- event/action information
- private organizer dashboard
- CSV exports

## Why this version uses Supabase

Do NOT store important petition/problem data in a local SQLite file on Streamlit Community Cloud.

Streamlit's documentation says Community Cloud does not guarantee persistence of local file storage. This project therefore uses a hosted Supabase PostgreSQL database so submissions remain stored independently of the Streamlit app's filesystem.

## 1. Create the database

Create a free Supabase project.

Open the project's SQL Editor and run the complete `schema.sql` file from this ZIP.

## 2. Get the Supabase credentials

From Supabase project settings/API, obtain:
- Project URL
- anon/public key
- service_role key

Keep the service_role key private. Never commit it to GitHub.

## 3. Put the project on GitHub

Upload:
- `app.py`
- `requirements.txt`
- `schema.sql`
- `README.md`
- `.gitignore`

Do NOT upload passwords or a secrets file.

## 4. Deploy to Streamlit Community Cloud

Create a Streamlit Community Cloud app:
- Repository: your GitHub repository
- Branch: main
- Main file: `app.py`
- Python: 3.12 is fine

Before deploying, open Advanced settings -> Secrets and add:

```toml
SUPABASE_URL = "https://YOUR_PROJECT.supabase.co"
SUPABASE_ANON_KEY = "YOUR_ANON_KEY"
SUPABASE_SERVICE_KEY = "YOUR_SERVICE_ROLE_KEY"
ADMIN_USER = "admin"
ADMIN_PASSWORD = "USE_A_LONG_RANDOM_PASSWORD"
```

Streamlit recommends storing secrets in Community Cloud's Secrets interface instead of committing them to GitHub.

## 5. Customize app.py

At the top change:
- COLLEGE_NAME
- SITE_NAME
- TAGLINE
- EVENT_TITLE
- EVENT_DATE
- EVENT_TIME
- EVENT_PLACE
- DEMANDS
- ORGANIZER_CONTACT
- SITE_OWNER
- YEAR

Also update the statement saying whether the platform is student-run / official.

## Features

### Students
- Home / overview
- Petition
- Private petition signing
- Live petition count
- Campus problem reporting
- Issue categories
- Optional contact details
- Ticket ID for issue follow-up
- Public status lookup
- Verified updates
- Regular-day student support
- Privacy and participation information

### Admin
- Password-protected dashboard
- Petition signatures
- Petition CSV download
- Problem-report database
- Problem-report CSV download
- Issue status updates
- Update publishing
- Basic dashboard counts

### Data durability

Petition signatures, issue reports and updates live in Supabase, not the Streamlit filesystem.
Therefore Streamlit app sleeping/restarting does not erase the database.

Keep the Supabase project active and retain your database backups.

## Security notes

- Never commit `SUPABASE_SERVICE_KEY`.
- Never commit admin passwords.
- Do not create public SELECT policies for petition signatures or private issue reports.
- Use a strong unique admin password.
- Collect only information you genuinely need.
- Review your college rules and applicable law before publishing.

## Copyright / ownership

The footer is configurable. Replace `SITE_OWNER` with the actual student organization or group responsible for the website.

Do not claim the website is an official college website unless you have authorization.

Copyright notice is informational and does not replace legal advice.

## Local run

Create a virtual environment:

```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
```

For local secrets, create `.streamlit/secrets.toml` (and never commit it):

```toml
SUPABASE_URL = "..."
SUPABASE_ANON_KEY = "..."
SUPABASE_SERVICE_KEY = "..."
ADMIN_USER = "admin"
ADMIN_PASSWORD = "..."
```
