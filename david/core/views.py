from django.contrib.auth import login
from django.contrib.auth import views as auth_views
from django.http import HttpResponse, HttpResponseServerError
from django.shortcuts import render, redirect
from django.template import loader
from django.urls import reverse_lazy
from django.views.decorators.cache import never_cache
from django.views.decorators.http import require_http_methods

from blog.models import Post
from .forms import (
    RegisterForm,
    LoginForm,
    ChangePasswordForm,
    ResetPasswordForm,
    ResetPasswordConfirmForm,
)


def index(request):
    """ context data """
    last_posts = (
        Post.objects.published()
        .select_related('author')
        .prefetch_related('categories')
        .order_by('-created_at')[:4]
    )

    return render(request, 'index.html', {
        'last_posts': last_posts
    })


@never_cache
@require_http_methods(["GET", "HEAD"])
def ping(request):
    """Réveil / keep-alive : appelée toutes les ~10 min par un service externe
    (UptimeRobot, cron-job.org...) pour que Render ne mette pas le serveur en veille.
    Volontairement ultra légère : pas de template, pas de base de données."""
    return HttpResponse("pong", content_type="text/plain")


def register(request):
    if request.user.is_authenticated:
        return redirect('core:index')

    if request.method == "POST":
        form = RegisterForm(request.POST)

        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('core:index')

    else:
        form = RegisterForm()

    return render(request, 'auth/register.html', {
        'form': form
    })


class LoginView(auth_views.LoginView):
    template_name = 'auth/login.html'
    authentication_form = LoginForm
    redirect_authenticated_user = True


class LogoutView(auth_views.LogoutView):
    next_page = reverse_lazy('core:index')


class PasswordChangeView(auth_views.PasswordChangeView):
    template_name = 'auth/password_change.html'
    form_class = ChangePasswordForm
    success_url = reverse_lazy('core:password_change_done')


class PasswordChangeDoneView(auth_views.PasswordChangeDoneView):
    template_name = 'auth/password_change_done.html'


class PasswordResetView(auth_views.PasswordResetView):
    template_name = 'auth/password_reset.html'
    email_template_name = 'auth/password_reset_email.txt'
    subject_template_name = 'auth/password_reset_subject.txt'
    form_class = ResetPasswordForm
    success_url = reverse_lazy('core:password_reset_done')


class PasswordResetDoneView(auth_views.PasswordResetDoneView):
    template_name = 'auth/password_reset_done.html'


class PasswordResetConfirmView(auth_views.PasswordResetConfirmView):
    template_name = 'auth/password_reset_confirm.html'
    form_class = ResetPasswordConfirmForm
    success_url = reverse_lazy('core:password_reset_complete')


class PasswordResetCompleteView(auth_views.PasswordResetCompleteView):
    template_name = 'auth/password_reset_complete.html'


# --- Pages d'erreur (utilisées seulement quand DEBUG=False) ---
# Branchées dans david/urls.py avec handler400 / handler403 / handler404 / handler500.

def bad_request(request, exception):
    return render(request, 'errors/400.html', status=400)


def permission_denied(request, exception):
    return render(request, 'errors/403.html', status=403)


def csrf_failure(request, reason=""):
    # Formulaire envoyé avec un jeton CSRF invalide/expiré -> même page 403
    return render(request, 'errors/403.html', status=403)


def page_not_found(request, exception):
    return render(request, 'errors/404.html', status=404)


def server_error(request):
    # Pas de render(request, ...) : on évite les context processors (user, messages...)
    # qui touchent la base de données, au cas où c'est elle qui est en panne.
    html = loader.get_template('errors/500.html').render()
    return HttpResponseServerError(html)
