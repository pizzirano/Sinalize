from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('signalsapi.urls')),
    path('catalog/', include('catalog.urls')),
    path('forms/', include('forms.urls')),
]

# Servir arquivos de mídia no modo DEBUG (imagens, vídeos, etc.)
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)