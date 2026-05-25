from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('django.contrib.auth.urls')),
    path('', RedirectView.as_view(url='/catalog/home/', permanent=False)),  # Redirecionamento
    path('catalog/', include('catalog.urls')),
    path('forms/', include('forms.urls')),
]

# Se estiver usando arquivos de mídia ou estáticos no dev
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
