from django.contrib import messages
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView, LogoutView, PasswordChangeView
from django.contrib.messages.views import SuccessMessageMixin
from django.core.paginator import Paginator
from django.core.signing import BadSignature
from django.db.models import Q
from django.http import Http404, HttpResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.template import TemplateDoesNotExist
from django.template.loader import get_template
from django.urls import reverse_lazy
from django.views.generic import UpdateView, CreateView, TemplateView, DeleteView

from mainapp.forms import ProfileEditForm, RegisterForm, SearchForm, BbForm, AiFormSet, UserCommentForm, \
    GuestCommentForm
from mainapp.models import AdvUser, SubRubric, Bb, Comment
from mainapp.utilities import signer


def index(request):
    bbs = Bb.objects.filter(is_active=True).select_related('rubric')[:10]
    context = {'bbs': bbs}
    return render(request, 'mainapp/index.html', context)


def other_page(request, page):
    try:
        template = get_template('mainapp/' + page + '.html')
    except TemplateDoesNotExist:
        raise Http404
    return HttpResponse(template.render(request=request))


@login_required
def profile(request):
    bbs = Bb.objects.filter(author=request.user.pk)
    context = {'bbs': bbs}
    return render(request, 'mainapp/profile.html', context)


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
    bb = Bb.objects.get(pk=pk)
    initial = {'bb': bb.pk}
    if request.user.is_authenticated:
        initial['author'] = request.user.username
        form_class = UserCommentForm
    else:
        form_class = GuestCommentForm
    form = form_class(initial=initial)
    if request.method == 'POST':
        c_form = form_class(request.POST)
        if c_form.is_valid():
            c_form.save()
            messages.add_message(request, messages.SUCCESS, 'Комментарий добавлен')
            return redirect(request.get_full_path_info())
        else:
            form = c_form
            messages.add_message(request, messages.WARNING, 'Комментарий не добавлен')
    ais = bb.additionalimage_set.all()
    comments = Comment.objects.filter(bb=pk, is_active=True)
    context = {'bb': bb, 'ais': ais, 'comments': comments, 'form': form}
    return render(request, 'mainapp/bb_detail.html', context)


@login_required
def profile_bb_detail(request, pk):
    bb = get_object_or_404(Bb, pk=pk)
    ais = bb.additionalimage_set.all()
    context = {'bb': bb, 'ais': ais}
    return render(request, 'mainapp/profile_bb_detail.html', context)


@login_required
def bb_add(request):
    if request.method == 'POST':
        form = BbForm(request.POST, request.FILES)
        if form.is_valid():
            bb = form.save()
            formset = AiFormSet(request.POST, request.FILES, instance=bb)
            if formset.is_valid():
                formset.save()
                messages.add_message(request, messages.SUCCESS, 'Объявление добавлено')
                return redirect('mainapp:profile')
    else:
        form = BbForm(initial={'author': request.user.pk})
        formset = AiFormSet()
    context = {'form': form, 'formset': formset}
    return render(request, 'mainapp/bb_add.html', context)


@login_required
def bb_edit(request, pk):
    bb = get_object_or_404(Bb, pk=pk)
    if request.method == 'POST':
        form = BbForm(request.POST, request.FILES, instance=bb)
        if form.is_valid():
            bb = form.save()
            formset = AiFormSet(request.POST, request.FILES, instance=bb)
            if formset.is_valid():
                formset.save()
                messages.add_message(request, messages.SUCCESS, 'Объявление исправлено')
                return redirect('mainapp:profile')
    else:
        form = BbForm(instance=bb)
        formset = AiFormSet(instance=bb)
    context = {'form': form, 'formset': formset}
    return render(request, 'mainapp/bb_edit.html', context)


@login_required
def bb_delete(request, pk):
    bb = get_object_or_404(Bb, pk=pk)
    if request.method == 'POST':
        bb.delete()
        messages.add_message(request, messages.SUCCESS, 'Объявление удалено')
        return redirect('mainapp:profile')
    else:
        context = {'bb': bb}
        return render(request, 'mainapp/bb_delete.html', context)
