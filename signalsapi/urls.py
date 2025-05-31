from django.urls import path 
from signalsapi.views import home

urlpatterns = [
    path('', home),

]