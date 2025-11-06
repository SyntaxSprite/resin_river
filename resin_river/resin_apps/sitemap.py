from django.contrib.sitemaps import Sitemap
from .models import Items


class ItemsSitemap(Sitemap):
    """Sitemap for Items"""
    changefreq = "weekly"
    priority = 0.8
    
    def items(self):
        return Items.objects.filter(available=True)
    
    def lastmod(self, obj):
        return obj.created_at
    
    def location(self, obj):
        return f'/post/{obj.slug}/'

