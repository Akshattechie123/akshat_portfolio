# Akshat Kumar Portfolio (Django)
## Local run
    python -m venv venv && source venv/bin/activate   # Windows: venv\Scripts\activate
    pip install -r requirements.txt
    cp .env.example .env        # fill EMAIL_HOST_PASSWORD
    python manage.py migrate
    python manage.py runserver
## Gmail App Password
Google Account > Security > enable 2-Step Verification > App passwords > create one > paste 16 chars in EMAIL_HOST_PASSWORD (no spaces).
Without it, emails print in the terminal (dev mode).
## Render deploy
Build: `./build.sh`   Start: `gunicorn config.wsgi`
Env: SECRET_KEY, DEBUG=False, ALLOWED_HOSTS=.onrender.com, CSRF_TRUSTED_ORIGINS=https://<app>.onrender.com, DASH_USER, DASH_PASSWORD, DATABASE_URL (Render Postgres), EMAIL_HOST_USER, EMAIL_HOST_PASSWORD, ADMIN_EMAIL
Note: Render free disk is ephemeral; uploaded images/PDFs/briefs vanish on redeploy. Use Render Disk or S3/Cloudinary for media.
