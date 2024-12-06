from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ImproperlyConfigured
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.views import View
from django.views.generic.edit import FormView, UpdateView
from django.urls import reverse
from tutorials.forms import LogInForm, PasswordForm, UserForm, SignUpForm
from tutorials.helpers import login_prohibited


@login_required
def dashboard(request):
    """Display the current user's dashboard based on account type."""
    current_user = request.user
    if current_user.account_type == "student":
        return redirect("student_dashboard")
    elif current_user.account_type == "tutor":
        return redirect("tutor_dashboard")
    return render(request, "dashboard.html", {"user": current_user})


@login_required
def student_dashboard(request):
    """Display the dashboard for students."""
    return render(request, 'student_dashboard.html', {'user': request.user})


@login_required
def tutor_dashboard(request):
    """Display the dashboard for tutors."""
    return render(request, 'tutor_dashboard.html', {'user': request.user})


@login_required
def view_bookings(request):
    """Display a calendar of the student's bookings."""
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':  # Check for AJAX request
        bookings = [
            {"title": "Math with John Doe", "start": "2024-12-10T10:00:00"},
            {"title": "Physics with Jane Smith", "start": "2024-12-15T14:00:00"},
        ]
        return JsonResponse(bookings, safe=False)

    return render(request, 'view_bookings_calendar.html')


@login_required
def view_tutor_bookings(request):
    """Display a calendar of the tutor's bookings."""
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':  # Check for AJAX request
        bookings = [
            {"title": "Lesson with Alice Johnson", "start": "2024-12-12T15:00:00"},
            {"title": "Lesson with Bob Smith", "start": "2024-12-13T10:00:00"},
        ]
        return JsonResponse(bookings, safe=False)

    return render(request, 'view_tutor_bookings_calendar.html')


@login_required
def request_booking(request):
    """Allow students to request a new booking."""
    if request.method == "POST":
        subject = request.POST.get("subject")
        date = request.POST.get("date")
        time = request.POST.get("time")
        messages.success(request, f"Booking request for {subject} on {date} at {time} has been submitted!")
        return redirect("student_dashboard")
    return render(request, 'request_booking.html')


@login_required
def change_language(request):
    """Allow tutors to change their teaching language."""
    if request.method == "POST":
        new_language = request.POST.get("language")
        if new_language:
            request.user.profile.teaching_language = new_language  # Assuming this field exists in the profile model
            request.user.profile.save()
            messages.success(request, f"Your teaching language has been updated to {new_language}.")
        else:
            messages.error(request, "Please select a valid language.")
        return redirect("tutor_dashboard")

    return render(request, "change_language.html")


@login_prohibited
def home(request):
    """Display the application's start/home screen."""
    return render(request, 'home.html')


class LoginProhibitedMixin:
    """Mixin that redirects when a user is logged in."""
    redirect_when_logged_in_url = None

    def dispatch(self, *args, **kwargs):
        if self.request.user.is_authenticated:
            return self.handle_already_logged_in(*args, **kwargs)
        return super().dispatch(*args, **kwargs)

    def handle_already_logged_in(self, *args, **kwargs):
        url = self.get_redirect_when_logged_in_url()
        return redirect(url)

    def get_redirect_when_logged_in_url(self):
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
        self.next = request.GET.get('next') or ''
        return self.render()

    def post(self, request):
        form = LogInForm(request.POST)
        self.next = request.POST.get('next') or settings.REDIRECT_URL_WHEN_LOGGED_IN
        user = form.get_user()
        if user is not None:
            login(request, user)
            return redirect("dashboard")
        messages.add_message(request, messages.ERROR, "The credentials provided were invalid!")
        return self.render()

    def render(self):
        form = LogInForm()
        return render(self.request, 'log_in.html', {'form': form, 'next': self.next})


def log_out(request):
    """Log out the current user."""
    logout(request)
    return redirect('home')


class PasswordView(LoginRequiredMixin, FormView):
    """Display password change screen and handle password change requests."""
    template_name = 'password.html'
    form_class = PasswordForm

    def get_form_kwargs(self, **kwargs):
        kwargs = super().get_form_kwargs(**kwargs)
        kwargs.update({'user': self.request.user})
        return kwargs

    def form_valid(self, form):
        form.save()
        login(self.request, self.request.user)
        return super().form_valid(form)

    def get_success_url(self):
        messages.add_message(self.request, messages.SUCCESS, "Password updated!")
        return reverse('dashboard')


class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    """Display user profile editing screen, and handle profile modifications."""
    model = UserForm
    template_name = "profile.html"
    form_class = UserForm

    def get_object(self):
        return self.request.user

    def get_success_url(self):
        messages.add_message(self.request, messages.SUCCESS, "Profile updated!")
        return reverse("dashboard")


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
        return reverse("dashboard")
