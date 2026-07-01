from django.urls import path
from django.views.generic import TemplateView
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('categoria/<int:categoria_id>/termos/', views.termo_list, name='termo_list'),
    path('subcategoria/<int:subcategoria_id>/termos/', views.termos_por_subcategoria, name='termos_por_subcategoria'),
    path('termo/<int:termo_id>/sinais/', views.sinal_list, name='sinal_list'),
    path('video/<int:video_id>/detalhe/', views.video_detail, name='video_detail'),
    path('search/', views.live_search, name='live_search'),
    path('termos/options/', views.termo_options, name='termo_options'),
    path('moderacao/', views.moderation_dashboard, name='moderation_dashboard'),
    path('moderacao/<str:object_type>/<int:object_id>/<str:action>/', views.moderation_action, name='moderation_action'),
    path('moderacao/categoria/<int:category_id>/<str:action>/', views.moderation_action_categoria, name='moderation_action_categoria'),
    path('moderacao/subcategoria/<int:subcategory_id>/<str:action>/', views.moderation_action_subcategoria, name='moderation_action_subcategoria'),

    # ✅ playground corrigido
    path(
        'playground/',
        TemplateView.as_view(template_name='catalog/pages/playground.html'),
        name='playground'
    ),
]