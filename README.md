
WhatsApp Requests - Fresh Django Project
---------------------------------------

What's included:
- Custom User model with username, user_id, profile_picture, primary/secondary phones & types
- Admin-only fields: is_satsangi (bool), is_ambrish (bool), department_notes (text)
- MediaRequest model with request_number: YYYYMMDD_HHMM_0001
- SiteSetting to store 3 Drive folder IDs (profile/reference/data)
- Google Drive helper (service account) for uploads & listing (optional)
- Templates for register/login/dashboard/request create
- Initial migrations included (core/migrations/0001_initial.py)

Quick start:
1. python3 -m venv .venv && source .venv/bin/activate
2. pip install -r requirements.txt
3. cp .env.example .env and edit values (GDRIVE_SERVICE_ACCOUNT_FILE if you want Drive uploads)
4. python3 manage.py migrate
5. python3 manage.py createsuperuser
6. python3 manage.py runserver
