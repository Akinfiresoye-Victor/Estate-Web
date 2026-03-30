
from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static 
from django.conf import settings 


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('core.urls')),
    path('customer/', include('estate.urls', namespace='customer')),
    path('members/', include('django.contrib.auth.urls')),
    path('accounts/', include('allauth.urls')),
    path('members/', include('members.urls')),
    path('executive/',include('admin_panel.urls')),
    path('agent/', include('agents.urls', namespace='agent')),
    path('company/', include('companies.urls', namespace='company')),
    path('landlord/', include('landlord.urls', namespace='landlord')),
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


admin.site.site_title="Admin Page" #The browsers title
admin.site.site_header="My Club Administration Page"
admin.site.index_title= "Welcome To THe admin Area......"

