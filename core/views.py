import os
from django.core.cache import cache
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.http import require_POST
from .emails import notify_admin, send_thanks
from .forms import BriefForm, ContactForm
from .models import BackendProject, ProjectFile, WebsiteProject

MAX_FILE = 10 * 1024 * 1024
ALLOWED_EXT = {".pdf", ".png", ".jpg", ".jpeg", ".doc", ".docx", ".txt", ".xlsx"}

def home(r):
    return render(r, "home.html", {"websites": WebsiteProject.objects.filter(is_published=True)[:3],
                                   "backends": BackendProject.objects.filter(is_published=True)[:3]})
def about(r): return render(r, "about.html")
def websites(r): return render(r, "websites.html", {"items": WebsiteProject.objects.filter(is_published=True)})
def backend(r): return render(r, "backend.html", {"items": BackendProject.objects.filter(is_published=True)})
def contact(r): return render(r, "contact.html")
def start(r): return render(r, "start.html")

def _ip(r):
    return (r.META.get("HTTP_X_FORWARDED_FOR", "").split(",")[0].strip()) or r.META.get("REMOTE_ADDR")

def _limited(r, key, limit=5):
    k = f"rl:{key}:{_ip(r)}"
    cache.add(k, 0, 3600)
    return cache.incr(k) > limit

def _errors(form):
    return {f: e[0] for f, e in form.errors.items()}

@require_POST
def contact_submit(r):
    if r.POST.get("website"): return JsonResponse({"ok": True})  # honeypot
    if _limited(r, "contact"): return JsonResponse({"ok": False, "error": "Too many requests. Try again in an hour."}, status=429)
    form = ContactForm(r.POST)
    if not form.is_valid(): return JsonResponse({"ok": False, "errors": _errors(form)}, status=400)
    obj = form.save(commit=False); obj.ip = _ip(r); obj.save()
    rows = [("Subject", obj.subject), ("Message", obj.message)]
    send_thanks(obj.email, obj.name, "Thanks for reaching out - Akshat Kumar",
                "Thanks for reaching out! I received your message and here's what you sent:", rows)
    notify_admin(f"New contact: {obj.name}", [("Name", obj.name), ("Email", obj.email), ("Phone", obj.phone)] + rows, obj.email)
    return JsonResponse({"ok": True})

@require_POST
def brief_submit(r):
    if r.POST.get("website"): return JsonResponse({"ok": True})  # honeypot
    if _limited(r, "brief"): return JsonResponse({"ok": False, "error": "Too many requests. Try again in an hour."}, status=429)
    data = r.POST.copy()
    chips = ", ".join(r.POST.getlist("feature_chips"))
    data["features"] = "\n".join(x for x in [chips, r.POST.get("features", "")] if x)
    form = BriefForm(data)
    files = r.FILES.getlist("files")
    errs = {}
    for f in files:
        if os.path.splitext(f.name)[1].lower() not in ALLOWED_EXT: errs["files"] = f"{f.name}: file type not allowed."
        elif f.size > MAX_FILE: errs["files"] = f"{f.name}: max 10MB."
    if not form.is_valid() or errs:
        return JsonResponse({"ok": False, "errors": {**_errors(form), **errs}}, status=400)
    b = form.save(commit=False); b.ip = _ip(r); b.save()
    for f in files[:5]: ProjectFile.objects.create(brief=b, file=f)
    rows = [("Project", b.title), ("Type", b.project_type), ("Goal", b.goal), ("Target users", b.target_users),
            ("Features", b.features), ("References", b.reference_links), ("Budget", b.budget),
            ("Timeline", b.timeline), ("Constraints", b.constraints)]
    send_thanks(b.email, b.full_name, "Thanks for reaching out - project brief received",
                "Thanks for sharing your project brief! Here's a summary of what you selected:", rows)
    atts = [(f.name, f.read(), f.content_type) for f in files[:5] if f.seek(0) is None]
    notify_admin(f"New project brief: {b.title or b.project_type} ({b.full_name})",
                 [("Name", b.full_name), ("Email", b.email), ("Phone", b.phone), ("Company", b.company)] + rows,
                 b.email, atts)
    return JsonResponse({"ok": True})
