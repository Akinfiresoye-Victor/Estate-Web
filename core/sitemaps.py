from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from core.models import PropertyManagementRent, PropertyManagementSale


class PropertyManagementRentSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.8

    def items(self):
        return PropertyManagementRent.objects.filter(is_listed=True)  # only show listed properties

    def location(self, item):
        return reverse('customer:view-property-s', args=[item.id])  # ✅ changed slug → id

    def lastmod(self, item):
        return item.last_updated  # ✅ correct field name from your model


class PropertyManagementSaleSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.8

    def items(self):
        return PropertyManagementSale.objects.filter(is_listed=True)  # only show listed properties

    def location(self, item):
        return reverse('customer:view-property-r', args=[item.id])  # ✅ changed slug → id

    def lastmod(self, item):
        return item.last_updated  # ✅ correct field name from your model


class StaticSitemap(Sitemap):
    changefreq = "monthly"
    priority = 0.6

    def items(self):
        return ['landing', 'about']  # adjust to your actual url names

    def location(self, item):
        return reverse(item)