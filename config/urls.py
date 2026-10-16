from django.conf import settings
from django.conf.urls.static import static
from django.contrib.sitemaps.views import sitemap
from django.urls import include, path
from django.views.generic import TemplateView
from core.sitemaps import StaticSitemap

urlpatterns = [
    path("dashboard/", include("core.dash_urls")),
    path("sitemap.xml", sitemap, {"sitemaps": {"s": StaticSitemap}}),
    path("robots.txt", TemplateView.as_view(template_name="robots.txt", content_type="text/plain")),
    path("", include("core.urls")),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
