from django.urls import path 
from forms.views import form

urlpatterns = [
    path('', form, name ='form'),

]