from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView, LogoutView, PasswordChangeView
from django.contrib.messages.views import SuccessMessageMixin
from django.core.paginator import Paginator
from django.core.signing import BadSignature
from django.db.models import Q
from django.http import Http404, HttpResponse
from django.shortcuts import render, get_object_or_404
from django.template import TemplateDoesNotExist
from django.template.loader import get_template
from django.urls import reverse_lazy
from django.views.generic import UpdateView, CreateView, TemplateView, DeleteView

from mainapp.forms import ProfileEditForm, RegisterForm, SearchForm
from mainapp.models import AdvUser, SubRubric, Bb
from mainapp.utilities import signer


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


class ProfileDeleteView(DeleteView, SuccessMessageMixin, LoginRequiredMixin):
    model = AdvUser
    template_name = 'mainapp/profile_delete.html'
    success_url = reverse_lazy('mainapp:index')
    success_message = 'Пользователь удален'

    def setup(self, request, *args, **kwargs):
        self.user_id = request.user.pk
        return super().setup(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        logout(request)
        return super().post(request, *args, **kwargs)

    def get_object(self, queryset=None):
        if not queryset:
            queryset = self.get_queryset()
        return get_object_or_404(queryset, pk=self.user_id)


def user_activate(request, sign):
    try:
        username = signer.unsign(sign)
    except BadSignature:
        return render(request, 'mainapp/activation_failed.html')
    user = get_object_or_404(AdvUser, username=username)
    if user.is_activated:
        template = 'mainapp/activation_done_earlier.html'
    else:
        template = 'mainapp/activation_done.html'
        user.is_active = True
        user.is_activated = True
        user.save()
    return render(request, template)


def rubric_bbs(request, pk):
    rubric = get_object_or_404(SubRubric, pk=pk)
    bbs = Bb.objects.filter(is_active=True, rubric=pk)
    if 'keyword' in request.GET:
        keyword = request.GET['keyword']
        q = Q(title__icontains=keyword) | Q(content__icontains=keyword)
        bbs = bbs.filter(q)
    else:
        keyword = ''
    form = SearchForm(initial={'keyword': keyword})
    paginator = Paginator(bbs, 2)
    if 'page' in request.GET:
        page_num = request.GET['page']
    else:
        page_num = 1
    page = paginator.get_page(page_num)
    context = {'rubric': rubric, 'page': page, 'bbs': page.object_list,
               'form': form}
    return render(request, 'mainapp/rubric_bbs.html', context)


def bb_detail(request, rubric_pk, pk):
    bb = get_object_or_404(Bb, pk=pk)
    ais = bb.additionalimage_set.all()
    context = {'bb': bb, 'ais': ais}
    return render(request, 'mainapp/bb_detail.html', context)
