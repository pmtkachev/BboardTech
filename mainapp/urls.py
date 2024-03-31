from django.conf import settings
from django.conf.urls.static import static
from django.urls import path

from .views import index, other_page, BbLoginView, profile, BbLogoutView, ProfileEditView, PasswordEditView, \
    RegisterView, RegisterDoneView, user_activate, ProfileDeleteView, rubric_bbs, bb_detail

app_name = 'mainapp'
urlpatterns = [
    path('', index, name='index'),
    path('accounts/profile/', profile, name='profile'),
    path('<int:rubric_pk>/<int:pk>/', bb_detail, name='bb_detail'),
    path('<int:pk>/', rubric_bbs, name='rubric_bbs'),
    path('<str:page>/', other_page, name='other'),
    path('accounts/login/', BbLoginView.as_view(), name='login'),
    path('accounts/logout/', BbLogoutView.as_view(), name='logout'),
    path('accounts/profile/edit/', ProfileEditView.as_view(), name='profile_edit'),
    path('accounts/profile/delete/', ProfileDeleteView.as_view(), name='profile_delete'),
    path('accounts/profile/password_edit/', PasswordEditView.as_view(), name='password_edit'),
    path('accounts/register/', RegisterView.as_view(), name='register'),
    path('accounts/register_done/', RegisterDoneView.as_view(), name='register_done'),
    path('accounts/profile/<str:sign>/', user_activate, name='user_activate'),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
