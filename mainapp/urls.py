from django.urls import path

from .views import index

app_name = 'mainapp'
urlpatterns = [
    path('', index, name='index'),
]
