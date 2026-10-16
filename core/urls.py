from django.urls import path
from . import views as v
urlpatterns = [
    path("", v.home, name="home"),
    path("about/", v.about, name="about"),
    path("websites/", v.websites, name="websites"),
    path("backend-projects/", v.backend, name="backend"),
    path("contact/", v.contact, name="contact"),
    path("start-a-project/", v.start, name="start"),
    path("api/contact/", v.contact_submit, name="contact_submit"),
    path("api/brief/", v.brief_submit, name="brief_submit"),
]
