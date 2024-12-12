
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('way/to/admin/', admin.site.urls),
    path('', include('oyiche_basic.urls', namespace='basic')),
    path('auth/', include('oyiche_auth.urls', namespace='auth')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

admin.site.site_header = "Oyiche School"
admin.site.site_title = "Oyiche School"
admin.site.index_title = "Welcome to Oyiche School"