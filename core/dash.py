import csv, hmac
from datetime import timedelta
from functools import wraps
from django.conf import settings
from django.core.cache import cache
from django.db.models import Q
from django.db.models.functions import TruncDate
from django.db.models import Count
from django.forms import modelform_factory
from django.http import Http404, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from .models import *

INBOX = {  # kind: (model, list columns, search fields)
    "briefs": (ProjectBrief, ["full_name", "email", "title", "project_type", "budget", "timeline"], ["full_name", "email", "company", "title", "goal", "features"]),
    "messages": (ContactMessage, ["name", "email", "subject", "phone"], ["name", "email", "subject", "message"]),
}
PROJ = {"websites": WebsiteProject, "backend": BackendProject}

def guard(fn):
    @wraps(fn)
    def w(r, *a, **k):
        if not r.session.get("dash"): return redirect("dash_login")
        return fn(r, *a, **k)
    return w

def R(r, tpl, ctx=None):
    ctx = ctx or {}
    ctx["new_briefs"] = ProjectBrief.objects.filter(status="new").count()
    ctx["new_msgs"] = ContactMessage.objects.filter(status="new").count()
    return render(r, tpl, ctx)

def login_view(r):
    err = ""
    if r.method == "POST":
        key = f"dl:{r.META.get('REMOTE_ADDR')}"; cache.add(key, 0, 900)
        if cache.incr(key) > 8: err = "Too many attempts. Wait 15 minutes."
        elif settings.DASH_PASSWORD and hmac.compare_digest(r.POST.get("u", ""), settings.DASH_USER) and \
             hmac.compare_digest(r.POST.get("p", ""), settings.DASH_PASSWORD):
            r.session["dash"] = True; cache.delete(key); return redirect("dash")
        else: err = "Wrong username or password." if settings.DASH_PASSWORD else "Set DASH_USER and DASH_PASSWORD in .env first."
    return render(r, "dash/login.html", {"err": err})

def logout_view(r):
    r.session.flush(); return redirect("dash_login")

@guard
def overview(r):
    since = timezone.now() - timedelta(days=6)
    days = {(since + timedelta(days=i)).date(): 0 for i in range(7)}
    for M in (ProjectBrief, ContactMessage):
        for x in M.objects.filter(created_at__gte=since).annotate(d=TruncDate("created_at")).values("d").annotate(n=Count("id")):
            if x["d"] in days: days[x["d"]] += x["n"]
    mx = max(days.values()) or 1
    chart = [{"d": k.strftime("%a"), "n": v, "h": int(v / mx * 100)} for k, v in days.items()]
    return R(r, "dash/overview.html", {
        "stats": [("Project briefs", ProjectBrief.objects.count()), ("New briefs", ProjectBrief.objects.filter(status="new").count()),
                  ("Messages", ContactMessage.objects.count()), ("New messages", ContactMessage.objects.filter(status="new").count())],
        "chart": chart, "briefs": ProjectBrief.objects.all()[:5], "msgs": ContactMessage.objects.all()[:5], "page": "home"})

@guard
def inbox(r, kind):
    if kind not in INBOX: raise Http404
    M, cols, sf = INBOX[kind]; qs = M.objects.all()
    q, st = r.GET.get("q", "").strip(), r.GET.get("status", "")
    if q:
        cond = Q()
        for f in sf: cond |= Q(**{f"{f}__icontains": q})
        qs = qs.filter(cond)
    if st: qs = qs.filter(status=st)
    rows = [{"obj": o, "cells": [getattr(o, c) for c in cols]} for o in qs]
    return R(r, "dash/list.html", {"kind": kind, "page": kind, "rows": rows, "q": q, "st": st, "status": STATUS,
             "heads": [M._meta.get_field(c).verbose_name.title() for c in cols]})

@guard
def detail(r, kind, pk):
    if kind not in INBOX: raise Http404
    o = get_object_or_404(INBOX[kind][0], pk=pk)
    if r.method == "POST":
        if "delete" in r.POST: o.delete(); return redirect("dash_inbox", kind=kind)
        if r.POST.get("status") in dict(STATUS): o.status = r.POST["status"]; o.save(update_fields=["status"])
        return redirect("dash_detail", kind=kind, pk=pk)
    skip = {"id", "status"}
    fields = [(f.verbose_name.title(), getattr(o, f.name)) for f in o._meta.fields if f.name not in skip and getattr(o, f.name)]
    return R(r, "dash/detail.html", {"o": o, "kind": kind, "page": kind, "fields": fields, "status": STATUS,
             "files": o.files.all() if kind == "briefs" else []})

@guard
def export(r, kind):
    if kind not in INBOX: raise Http404
    M = INBOX[kind][0]; names = [f.name for f in M._meta.fields]
    resp = HttpResponse(content_type="text/csv"); resp["Content-Disposition"] = f"attachment; filename={kind}.csv"
    w = csv.writer(resp); w.writerow(names)
    for o in M.objects.all(): w.writerow([getattr(o, n) for n in names])
    return resp

@guard
def proj_list(r, kind):
    if kind not in PROJ: raise Http404
    return R(r, "dash/projects.html", {"kind": kind, "page": "p" + kind, "items": PROJ[kind].objects.all()})

@guard
def proj_form(r, kind, pk=None):
    if kind not in PROJ: raise Http404
    M = PROJ[kind]; o = get_object_or_404(M, pk=pk) if pk else None
    F = modelform_factory(M, fields="__all__")
    f = F(r.POST or None, r.FILES or None, instance=o)
    if r.method == "POST" and f.is_valid(): f.save(); return redirect("dash_proj", kind=kind)
    return R(r, "dash/form.html", {"form": f, "kind": kind, "page": "p" + kind, "editing": bool(o)})

@guard
def proj_delete(r, kind, pk):
    if kind not in PROJ: raise Http404
    if r.method == "POST": get_object_or_404(PROJ[kind], pk=pk).delete()
    return redirect("dash_proj", kind=kind)
