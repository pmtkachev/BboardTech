from django.urls import path

from .views import index, other_page, BbLoginView, profile, BbLogoutView, ProfileEditView, PasswordEditView, \
    RegisterView, RegisterDoneView, user_activate

app_name = 'mainapp'
urlpatterns = [
    path('', index, name='index'),
    path('accounts/profile/', profile, name='profile'),
    path('<str:page>/', other_page, name='other'),
    path('accounts/profile/<str:sign>/', user_activate, name='user_activate'),
    path('accounts/login/', BbLoginView.as_view(), name='login'),
    path('accounts/logout/', BbLogoutView.as_view(), name='logout'),
    path('accounts/profile/edit/', ProfileEditView.as_view(), name='profile_edit'),
    path('accounts/profile/password_edit/', PasswordEditView.as_view(), name='password_edit'),
    path('accounts/register/', RegisterView.as_view(), name='register'),
    path('accounts/register_done/', RegisterDoneView.as_view(), name='register_done'),
]
