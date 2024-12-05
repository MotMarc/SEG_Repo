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
from tutorials.forms import LogInForm, PasswordForm, UserForm, SignUpForm, UserForm, SignUpForm, TutorProfileForm, BookingForm, AdminBookingForm
from tutorials.helpers import login_prohibited
from django.http import HttpResponseForbidden, HttpResponseBadRequest
from .models import User, Booking, Tutor, Language, Term, Lesson
from django.contrib.admin.views.decorators import staff_member_required
from django.core.exceptions import ValidationError


@login_required
def dashboard(request):
    """Display the current user's dashboard."""

    current_user = request.user
    return render(request, 'dashboard.html', {'user': current_user})

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
    """Allow students to create a booking with a tutor."""
    if request.method == 'POST':
        form = BookingForm(request.POST)
        if form.is_valid():
            try:
                booking = form.save(commit=False)
                booking.student = request.user
                booking.save()
                messages.success(request, "Booking created successfully!")
                return redirect('dashboard')
            except ValidationError as e:
                form.add_error(None, e)  # Add the error to the form
        else:
            messages.error(request, "Please correct the errors.")
    else:
        form = BookingForm()

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
    """Allow tutors to select the languages and specializations they can teach."""
    user = request.user

    if not user.is_tutor:
        messages.error(request, "You must be a tutor to access this page.")
        return redirect('dashboard')

    tutor = user.tutor

    if request.method == 'POST':
        form = TutorProfileForm(request.POST, instance=tutor)
        if form.is_valid():
            form.save()
            messages.success(request, "Your teaching profile has been updated.")
            return redirect('dashboard')
    else:
        form = TutorProfileForm(instance=tutor)

    return render(request, 'tutor_profile.html', {'form': form})

@staff_member_required
def admin_create_booking(request):
    if request.method == 'POST':
        form = AdminBookingForm(request.POST)
        if form.is_valid():
            booking = form.save(commit=False)
            booking.status = Booking.PENDING  # Booking is pending admin approval
            booking.student_approval = Booking.PENDING_APPROVAL  # Mark as pending student approval
            booking.save()
            messages.success(request, "Booking created successfully! Awaiting student approval.")
            return redirect('admin_pending_bookings')
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = AdminBookingForm()
    return render(request, 'admin_create_booking.html', {'form': form})

@login_required
def view_bookings(request):
    """Display all bookings for the logged-in user."""
    bookings = Booking.objects.filter(student=request.user).order_by('term__start_date', 'day_of_week', 'start_time')
    return render(request, 'view_bookings.html', {'bookings': bookings})


@login_required
def pending_student_bookings(request):
    """Display bookings awaiting student approval."""
    student = request.user
    if not student.is_authenticated or student.is_staff:
        return HttpResponseForbidden("Only students can access this page.")

    pending_bookings = Booking.objects.filter(student=student, student_approval=Booking.PENDING_APPROVAL)
    return render(request, 'pending_student_bookings.html', {'pending_bookings': pending_bookings})


@login_required
def student_approve_booking(request, booking_id):
    """Handle student approval or rejection of a booking."""
    booking = get_object_or_404(Booking, id=booking_id, student=request.user)

    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'approve':
            booking.student_approval = Booking.APPROVED
            booking.status = Booking.ACCEPTED  # Optionally update the status to Accepted
            booking.save()
            messages.success(request, "Booking approved successfully!")
        elif action == 'reject':
            booking.student_approval = Booking.REJECTED
            booking.status = Booking.DECLINED  # Optionally update the status to Declined
            booking.save()
            messages.success(request, "Booking rejected successfully!")
        else:
            messages.error(request, "Invalid action.")
    
    return redirect('pending_student_bookings')