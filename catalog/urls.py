from django.urls import path
from . import views

urlpatterns = [
    path('dominio/', views.dominio_list, name='dominio-list'),
    path('dominio/<int:dominio_id>/categorias/', views.categoria_list, name='categoria-list'),
    path('dominio/<int:dominio_id>/categoria/<int:categoria_id>/subcategorias/', views.subcategoria_list, name='subcategoria-list'),
    path('dominio/<int:dominio_id>/categoria/<int:categoria_id>/subcategoria/<int:subcategoria_id>/termos/', views.termo_list, name='termo-list'),
    path('dominio/<int:dominio_id>/categoria/<int:categoria_id>/subcategoria/<int:subcategoria_id>/termo/<int:termo_id>/', views.termo_detail, name='termo-detail'),
]