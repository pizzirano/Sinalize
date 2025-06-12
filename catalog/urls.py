from django.urls import path
from . import views

urlpatterns = [
    #path('dominio/', views.dominio_list, name='dominio-list'),
    #path('dominio/<int:dominio_id>/categorias/', views.categoria_list, name='categoria-list'),
    #path('dominio/<int:dominio_id>/categoria/<int:categoria_id>/subcategorias/', views.subcategoria_list, name='subcategoria-list'),
    path('categoria/<int:categoria_id>/termos/', views.termo_list, name='termo_list'),
    path('sinal/', views.sinal_detail, name='sinal-detail'),
    path('home/', views.home, name='home'),
    path('subcategoria/<int:subcategoria_id>/termos/', views.termos_por_subcategoria, name='termos_por_subcategoria'),
    path('termo/<int:termo_id>/sinais/', views.sinal_list, name='sinal_list'),
   # path('category/', views.category, name='category'),
         
]