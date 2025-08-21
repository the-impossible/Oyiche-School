
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from debug_toolbar.toolbar import debug_toolbar_urls

urlpatterns = [
    path('way/to/admin/', admin.site.urls),
    path('', include('oyiche_basic.urls', namespace='basic')),
    path('auth/', include('oyiche_auth.urls', namespace='auth')),
    path('sch/', include('oyiche_schMGT.urls', namespace='sch')),
    path('payment/', include('oyiche_payment.urls', namespace='payment')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += debug_toolbar_urls()

admin.site.site_header = "Oyiche Academy"
admin.site.site_title = "Oyiche Academy"
admin.site.index_title = "Welcome to Oyiche Academy"