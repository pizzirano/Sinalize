from django.urls import path
from . import views

app_name = 'forms'

urlpatterns = [
    path('cadastrar-termo/', views.cadastrar_termo_e_videos, name='cadastrar_termo'),
    path('adicionar-videos/', views.adicionar_videos_a_termo, name='adicionar_videos'),
    path('minhas-submissoes/', views.my_submissions, name='my_submissions'),
    path('editar-termo/<int:termo_id>/', views.editar_termo, name='editar_termo'),
    path('subcategorias/', views.subcategorias_por_categoria, name='subcategorias_por_categoria'),
    path('login/', views.login_view, name='login'),
    path('register/', views.register, name='register'),
]