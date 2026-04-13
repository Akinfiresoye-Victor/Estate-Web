from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static 
from django.conf import settings 
from allauth.account.views import EmailView
from django.urls import reverse_lazy
from members.views import resend_verification, CustomEmailView,logout_for_email_change

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
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


admin.site.site_title="Admin Page" #The browsers title
admin.site.site_header="My Club Administration Page"
admin.site.index_title= "Welcome To THe admin Area......"

