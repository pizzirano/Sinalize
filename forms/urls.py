from django.urls import path
from . import views

urlpatterns = [
    path('cadastrar-termo/', views.cadastrar_termo_e_videos, name='cadastrar_termo'),
]