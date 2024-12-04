from django.conf import settings
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ImproperlyConfigured
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views import View
from django.views.generic.edit import FormView, UpdateView
from tutorials.forms import LogInForm, PasswordForm, SignUpForm, UserForm
from tutorials.helpers import login_prohibited

from .models import (Invoice, Lesson, LessonRequest, TutorApplication,
                     UserProfile)


@staff_member_required
def review_tutor_application(request, application_id, action):
    """Allow admins to approve or reject tutor applications."""
    application = get_object_or_404(TutorApplication, id=application_id)
    if action == 'approve':
        application.status = 'approved'
        application.user.profile.role = 'tutor'
        application.user.profile.save()
    elif action == 'reject':
        application.status = 'rejected'
    application.save()
    messages.success(request, f"The application has been {action}d.")
    return redirect('admin_dashboard')

@login_required
def apply_tutor(request):
    """Allow users to apply to become a tutor."""
    user = request.user
    if hasattr(user, 'tutor_application'):
        messages.error(request, "You have already applied to become a tutor.")
        return redirect('dashboard')

    TutorApplication.objects.create(user=user)
    messages.success(request, "Your application to become a tutor has been submitted.")
    return redirect('dashboard')

@login_required
def dashboard(request):
    """Display the current user's dashboard with detailed information."""

    current_user = request.user
    congratulation_message = "Welcome to your personalized dashboard!"

    # 获取用户额外信息
    profile = get_object_or_404(UserProfile, user=current_user)

    # 获取用户相关数据
    lesson_requests = LessonRequest.objects.filter(student=current_user)
    lessons_as_tutor = Lesson.objects.filter(tutor=current_user)
    invoices = Invoice.objects.filter(lesson__tutor=current_user)

    # Tutor 申请状态
    tutor_application = None
    if hasattr(current_user, 'tutor_application'):
        tutor_application = current_user.tutor_application

    context = {
        'user': current_user,
        'profile': profile,
        'lesson_requests': lesson_requests,
        'lessons_as_tutor': lessons_as_tutor,
        'invoices': invoices,
        'congratulation_message': congratulation_message,
        'tutor_application': tutor_application,
    }
    return render(request, 'dashboard.html', context)


@login_prohibited
def home(request):
    """Display the application's start/home screen."""

    return render(request, 'home.html')


class LoginProhibitedMixin:
    """Mixin that redirects when a user is logged in."""

    redirect_when_logged_in_url = None

    def dispatch(self, *args, **kwargs):
        """Redirect when logged in, or dispatch as normal otherwise."""
        if self.request.user.is_authenticated:
            return self.handle_already_logged_in(*args, **kwargs)
        return super().dispatch(*args, **kwargs)

    def handle_already_logged_in(self, *args, **kwargs):
        url = self.get_redirect_when_logged_in_url()
        return redirect(url)

    def get_redirect_when_logged_in_url(self):
        """Returns the url to redirect to when not logged in."""
        if self.redirect_when_logged_in_url is None:
            raise ImproperlyConfigured(
                "LoginProhibitedMixin requires either a value for "
                "'redirect_when_logged_in_url', or an implementation for "
                "'get_redirect_when_logged_in_url()'."
            )
        else:
            return self.redirect_when_logged_in_url


class LogInView(LoginProhibitedMixin, View):
    """Display login screen and handle user login."""

    http_method_names = ['get', 'post']
    redirect_when_logged_in_url = settings.REDIRECT_URL_WHEN_LOGGED_IN

    def get(self, request):
        """Display log in template."""

        self.next = request.GET.get('next') or ''
        return self.render()

    def post(self, request):
        """Handle log in attempt."""

        form = LogInForm(request.POST)
        self.next = request.POST.get('next') or settings.REDIRECT_URL_WHEN_LOGGED_IN
        user = form.get_user()
        if user is not None:
            login(request, user)
            return redirect(self.next)
        messages.add_message(request, messages.ERROR, "The credentials provided were invalid!")
        return self.render()

    def render(self):
        """Render log in template with blank log in form."""

        form = LogInForm()
        return render(self.request, 'log_in.html', {'form': form, 'next': self.next})


def log_out(request):
    """Log out the current user"""

    logout(request)
    return redirect('home')


class PasswordView(LoginRequiredMixin, FormView):
    """Display password change screen and handle password change requests."""

    template_name = 'password.html'
    form_class = PasswordForm

    def get_form_kwargs(self, **kwargs):
        """Pass the current user to the password change form."""

        kwargs = super().get_form_kwargs(**kwargs)
        kwargs.update({'user': self.request.user})
        return kwargs

    def form_valid(self, form):
        """Handle valid form by saving the new password."""

        form.save()
        login(self.request, self.request.user)
        return super().form_valid(form)

    def get_success_url(self):
        """Redirect the user after successful password change."""

        messages.add_message(self.request, messages.SUCCESS, "Password updated!")
        return reverse('dashboard')


class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    """Display user profile editing screen, and handle profile modifications."""

    model = UserForm
    template_name = "profile.html"
    form_class = UserForm

    def get_object(self):
        """Return the object (user) to be updated."""
        user = self.request.user
        return user

    def get_success_url(self):
        """Return redirect URL after successful update."""
        messages.add_message(self.request, messages.SUCCESS, "Profile updated!")
        return reverse(settings.REDIRECT_URL_WHEN_LOGGED_IN)


class SignUpView(LoginProhibitedMixin, FormView):
    """Display the sign up screen and handle sign ups."""

    form_class = SignUpForm
    template_name = "sign_up.html"
    redirect_when_logged_in_url = settings.REDIRECT_URL_WHEN_LOGGED_IN

    def form_valid(self, form):
        self.object = form.save()
        login(self.request, self.object)
        return super().form_valid(form)

    def get_success_url(self):
        return reverse(settings.REDIRECT_URL_WHEN_LOGGED_IN)


