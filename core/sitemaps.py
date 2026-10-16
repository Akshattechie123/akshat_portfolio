from django.contrib.sitemaps import Sitemap
from django.urls import reverse
class StaticSitemap(Sitemap):
    priority = 0.8
    def items(self): return ["home", "about", "websites", "backend", "contact", "start"]
    def location(self, item): return reverse(item)
