Share the project and database with a friend

Option A — Share repo + db.sqlite3 (simple)
- Add db.sqlite3 to the repo (NOT recommended for public repos) or send the file separately via e.g. Google Drive/OneDrive.
- Steps for your friend (PowerShell):

```powershell
# clone the repo
git clone <REPO_URL>
cd mou_manager
# create and activate a virtualenv
python -m venv .venv
.\.venv\Scripts\Activate.ps1
# install deps
pip install -r requirements.txt
# copy .env.example to .env and update values if needed
copy .env.example .env
# (if you're sending db.sqlite3 separately) place it in the project root next to manage.py
# run migrations (skip if you include db.sqlite3 and don't want to overwrite)
python .\manage.py migrate
# create a superuser (optional)
python .\manage.py createsuperuser
# run server
python .\manage.py runserver
```

Notes for Option A:
- If you include `db.sqlite3`, your friend can skip `migrate` and `createsuperuser` (unless they want to recreate users).
- Do NOT push `.env` to source control; use `.env.example` as template.

Option B — Share repo + fixture (recommended for public sharing)
- Dump data from your DB into a fixture file (JSON) and share the fixture instead of the raw sqlite file.

On your machine (create the fixture):

```powershell
# from project root
python .\manage.py dumpdata --natural-primary --natural-foreign --indent 2 > full_fixture.json
```

- Send `full_fixture.json` to your friend.

Friend's steps (PowerShell):

```powershell
git clone <REPO_URL>
cd mou_manager
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy .env.example .env
python .\manage.py migrate
python .\manage.py loaddata full_fixture.json
python .\manage.py runserver
```

Security and size notes
- db.sqlite3 can be large and may contain sensitive data; prefer a fixture that you scrub.
- If using cloud-sharing, prefer expiring links.

Troubleshooting
- If you get import errors, ensure you activated the venv used to install packages.
- If the PDF endpoint errors about missing backends (Tcl/Tk), ensure `matplotlib` is installed and the app uses `matplotlib.use('Agg')` (already in code).

