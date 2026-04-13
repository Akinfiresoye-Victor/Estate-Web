from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from core.models import PropertyManagementRent, PropertyManagementSale


class PropertyManagementRentSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.8

    def items(self):
        return PropertyManagementRent.objects.filter(is_listed=True).order_by('-listed_date')

    def location(self, item):
        # ✅ matches → /property_view/rent/<property_id>/
        return reverse('customer:view-property-r', args=[item.id])

    def lastmod(self, item):
        return item.last_updated


class PropertyManagementSaleSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.8

    def items(self):
        return PropertyManagementSale.objects.filter(is_listed=True).order_by('-listed_date')

    def location(self, item):
        # ✅ matches → /property_view/sale/<property_id>/
        return reverse('customer:view-property-s', args=[item.id])

    def lastmod(self, item):
        return item.last_updated


class StaticSitemap(Sitemap):
    changefreq = "monthly"
    priority = 0.6

    def items(self):
        return [
            'landing',
            'about',
            'faq',
            'articles',
            'estate-blog',
            'partner-with-us',
            'feedback',
        ]

    def location(self, item):
        return reverse(item)