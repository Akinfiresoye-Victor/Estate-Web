from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static 
from django.conf import settings 
from members.views import resend_verification, CustomEmailView,logout_for_email_change
from core.sitemaps import (
    PropertyManagementRentSitemap,
    PropertyManagementSaleSitemap,
    StaticSitemap,
)
from django.contrib.sitemaps.views import sitemap
from django.http import HttpResponse



# combine all sitemaps into one dictionary
sitemaps = {
    'rent': PropertyManagementRentSitemap,
    'sale': PropertyManagementSaleSitemap,
    'static': StaticSitemap,
}



# robots.txt view — keep it here to avoid creating a separate file
def robots_txt(request):
    content = """User-agent: *
Allow: /
Sitemap: https://estatewebng.com/sitemap.xml
"""
    return HttpResponse(content, content_type="text/plain")

#yeah
urlpatterns = [
    path(f'{settings.DJANGO_ADMIN_PATH}/', admin.site.urls),
    path('', include('core.urls')),
    path('customer/', include('estate.urls', namespace='customer')),
    path('accounts/email/', CustomEmailView.as_view(), name='account_email'),
    path('members/', include('django.contrib.auth.urls')),
    path('accounts/resend-verification/', resend_verification, name='resend_verification'),
    path('accounts/', include('allauth.urls')),
    path('members/', include('members.urls')),
    path(f'{settings.ADMIN_SECRET_PATH}/', include('admin_panel.urls', namespace='control_panel')),
    path('agent/', include('agents.urls', namespace='agent')),
    path('company/', include('companies.urls', namespace='company')),
    path('landlord/', include('landlord.urls', namespace='landlord')),
    path('accounts/email/change/', logout_for_email_change, name='logout_for_email_change'),
    path('sitemap.xml', sitemap, {'sitemaps': sitemaps}, name='django.contrib.sitemaps.views.sitemap'),
    path('robots.txt', robots_txt, name='robots_txt'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


admin.site.site_title="Admin Page" #The browsers title
admin.site.site_header="My Club Administration Page"
admin.site.index_title= "Welcome To THe admin Area......"




