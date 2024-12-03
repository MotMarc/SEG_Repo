from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ImproperlyConfigured
from django.shortcuts import redirect, render, get_object_or_404
from django.views import View
from django.views.generic.edit import FormView, UpdateView
from django.urls import reverse
from tutorials.forms import LogInForm, PasswordForm, UserForm, SignUpForm, UserForm, SignUpForm, TutorProfileForm, BookingForm
from tutorials.helpers import login_prohibited
from django.http import HttpResponseForbidden, HttpResponseBadRequest
from .models import User, Booking, Tutor, Language, Term, Lesson
from django.contrib.admin.views.decorators import staff_member_required


@login_required
def dashboard(request):
    """Display the current user's dashboard."""

    current_user = request.user
    return render(request, 'dashboard.html', {'user': current_user})

    # if user.is_tutor:
    #     # User is a tutor; fetch their lessons
    #     lessons = Lesson.objects.filter(booking__tutor__user=user).order_by('date', 'start_time')
    #     return render(request, 'tutor_dashboard.html', {'lessons': lessons})
    # else:
    #     # User is a student; fetch their bookings
    #     bookings = Booking.objects.filter(student=user).order_by('term__start_date')
    #     return render(request, 'student_dashboard.html', {'bookings': bookings})


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


#Handle the creation of a booking with a tutor.
@login_required
def create_booking(request):
    if request.method == 'POST':
        form = BookingForm(request.POST)
        if form.is_valid():
            booking = form.save(commit=False)
            booking.student = request.user  # Attach the logged-in user as the student
            booking.save()
            messages.success(request, "Your booking was successfully created!")
            return redirect('dashboard')
    else:
        form = BookingForm()
        form.fields['tutor'].queryset = Tutor.objects.all()  # Restrict tutors to active ones

    return render(request, 'create_booking.html', {'form': form})


#pending booking views
@staff_member_required
def pending_bookings(request):
    """Display all pending bookings for admin users."""
    bookings = Booking.objects.filter(status=Booking.PENDING).order_by('term__start_date')
    return render(request, 'admin_pending_bookings.html', {'bookings': bookings})

#accept booking
@staff_member_required
def approve_booking(request, booking_id):
    """Approve a specific booking and generate lessons."""
    booking = get_object_or_404(Booking, id=booking_id, status=Booking.PENDING)
    booking.status = Booking.ACCEPTED
    booking.save()
    # Optionally, generate lessons or send notifications here
    messages.success(request, f"Booking with ID {booking_id} has been approved.")
    return redirect('admin_pending_bookings')

#reject booking
@staff_member_required
def decline_booking(request, booking_id):
    """Decline a specific booking."""
    booking = get_object_or_404(Booking, id=booking_id, status=Booking.PENDING)
    booking.status = Booking.DECLINED
    booking.save()
    messages.success(request, f"Booking with ID {booking_id} has been declined.")
    return redirect('admin_pending_bookings')


#update booking view(only admins)
@login_required
def update_booking_status(request, booking_id, new_status):
    """Allow only admins to update the status of a booking."""
    if not request.user.is_staff:
        return HttpResponseForbidden("You are not allowed to perform this action.")

    booking = get_object_or_404(Booking, id=booking_id)

    if new_status not in [Booking.ACCEPTED, Booking.DECLINED]:
        return HttpResponseBadRequest("Invalid status.")

    booking.status = new_status
    booking.save()
    messages.success(request, f"Booking has been {new_status.lower()}.")
    return redirect('admin_pending_bookings')

#...
@login_required
def tutor_profile(request):
    """Allow tutors to select the languages they can teach."""
    user = request.user

    # Check if the user is a tutor
    if not user.is_tutor:
        messages.error(request, "You must be a tutor to access this page.")
        return redirect('dashboard')

    tutor = user.tutor  # Get the Tutor instance associated with the user

    if request.method == 'POST':
        form = TutorProfileForm(request.POST, instance=tutor)
        if form.is_valid():
            form.save()
            messages.success(request, "Your teaching languages have been updated.")
            return redirect('dashboard')
    else:
        form = TutorProfileForm(instance=tutor)

    return render(request, 'tutor_profile.html', {'form': form})
