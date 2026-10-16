import logging, threading
from django.conf import settings
from django.core.mail import EmailMessage, EmailMultiAlternatives
from django.template.loader import render_to_string

log = logging.getLogger(__name__)

def _run(fn):
    def wrapper():
        try: fn()
        except Exception: log.exception("Email sending failed (data is safe in DB)")
    threading.Thread(target=wrapper, daemon=True).start()

def send_thanks(to, name, subject, intro, rows):
    """User ko branded 'thanks' email, usme unka selected data."""
    def go():
        ctx = {"name": name, "intro": intro, "rows": [(k, v) for k, v in rows if v]}
        html = render_to_string("emails/thanks.html", ctx)
        text = f"Hi {name},\n\n{intro}\n\n" + "\n".join(f"{k}: {v}" for k, v in ctx["rows"]) + \
               "\n\nI'll reply within 24-48 hours.\n\n- Akshat Kumar"
        m = EmailMultiAlternatives(subject, text, settings.DEFAULT_FROM_EMAIL, [to])
        m.attach_alternative(html, "text/html")
        m.send()
    _run(go)

def notify_admin(subject, rows, reply_to, attachments=()):
    def go():
        body = "\n".join(f"{k}: {v}" for k, v in rows if v)
        m = EmailMessage(subject, body, settings.DEFAULT_FROM_EMAIL, [settings.ADMIN_EMAIL], reply_to=[reply_to])
        for name, data, mime in attachments: m.attach(name, data, mime)
        m.send()
    _run(go)
