
from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static 
from django.conf import settings 


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('estate.urls')),
    path('members/', include('django.contrib.auth.urls')),
    path('members/', include('members.urls')),
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


admin.site.site_title="Admin Page" #The browsers title
admin.site.site_header="My Club Administration Page"
admin.site.index_title= "Welcome To THe admin Area......"