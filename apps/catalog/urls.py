from django.urls import path
from django.views.generic import TemplateView
from . import views

urlpatterns = [
    path('home/', views.home, name='home'),
    path('categoria/<int:categoria_id>/termos/', views.termo_list, name='termo_list'),
    path('subcategoria/<int:subcategoria_id>/termos/', views.termos_por_subcategoria, name='termos_por_subcategoria'),
    path('termo/<int:termo_id>/sinais/', views.sinal_list, name='sinal_list'),
    path('video/<int:video_id>/detalhe/', views.video_detail, name='video_detail'),

    # ✅ playground corrigido
    path(
        'playground/',
        TemplateView.as_view(template_name='catalog/pages/playground.html'),
        name='playground'
    ),
]