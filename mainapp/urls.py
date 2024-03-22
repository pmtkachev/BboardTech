from django.urls import path

from .views import index, other_page, BbLoginView, profile, BbLogoutView

app_name = 'mainapp'
urlpatterns = [
    path('', index, name='index'),
    path('accounts/profile/', profile, name='profile'),
    path('<str:page>/', other_page, name='other'),
    path('accounts/login/', BbLoginView.as_view(), name='login'),
    path('accounts/logout/', BbLogoutView.as_view(), name='logout'),
]
