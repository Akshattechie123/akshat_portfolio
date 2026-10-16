from django.urls import path
from . import dash as d
urlpatterns = [
    path("", d.overview, name="dash"),
    path("login/", d.login_view, name="dash_login"),
    path("logout/", d.logout_view, name="dash_logout"),
    path("export/<str:kind>/", d.export, name="dash_export"),
    path("projects/<str:kind>/", d.proj_list, name="dash_proj"),
    path("projects/<str:kind>/new/", d.proj_form, name="dash_proj_new"),
    path("projects/<str:kind>/<int:pk>/edit/", d.proj_form, name="dash_proj_edit"),
    path("projects/<str:kind>/<int:pk>/delete/", d.proj_delete, name="dash_proj_del"),
    path("<str:kind>/", d.inbox, name="dash_inbox"),
    path("<str:kind>/<int:pk>/", d.detail, name="dash_detail"),
]
