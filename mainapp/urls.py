from django.urls import path
from mainapp import views as mainapp

app_name = 'main'

urlpatterns = [
    path('', mainapp.index, name='index'),
]
