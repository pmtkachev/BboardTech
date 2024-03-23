from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView, LogoutView, PasswordChangeView
from django.contrib.messages.views import SuccessMessageMixin
from django.http import Http404, HttpResponse
from django.shortcuts import render, get_object_or_404
from django.template import TemplateDoesNotExist
from django.template.loader import get_template
from django.urls import reverse_lazy
from django.views.generic import UpdateView, CreateView, TemplateView

from mainapp.forms import ProfileEditForm, RegisterForm
from mainapp.models import AdvUser


def index(request):
    return render(request, 'mainapp/index.html')


def other_page(request, page):
    try:
        template = get_template('mainapp/' + page + '.html')
    except TemplateDoesNotExist:
        raise Http404
    return HttpResponse(template.render(request=request))


@login_required
def profile(request):
    return render(request, 'mainapp/profile.html')


class BbLoginView(LoginView):
    template_name = 'mainapp/login.html'


class BbLogoutView(LogoutView):
    pass


class ProfileEditView(SuccessMessageMixin, LoginRequiredMixin, UpdateView):
    model = AdvUser
    template_name = 'mainapp/profile_edit.html'
    form_class = ProfileEditForm
    success_url = reverse_lazy('mainapp:profile')
    success_message = 'Данные пользователя изменены'

    def setup(self, request, *args, **kwargs):
        self.user_id = request.user.pk
        return super().setup(request, *args, **kwargs)

    def get_object(self, queryset=None):
        if not queryset:
            queryset = self.get_queryset()
        return get_object_or_404(queryset, pk=self.user_id)


class PasswordEditView(SuccessMessageMixin, LoginRequiredMixin, PasswordChangeView):
    template_name = 'mainapp/password_edit.html'
    success_url = reverse_lazy('mainapp:profile')
    success_message = 'Пароль успешно изменен'


class RegisterView(CreateView):
    model = AdvUser
    template_name = 'mainapp/register.html'
    form_class = RegisterForm
    success_url = reverse_lazy('mainapp:register_done')


class RegisterDoneView(TemplateView):
    template_name = 'mainapp/register_done.html'
