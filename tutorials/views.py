# tutorials/views.py

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ImproperlyConfigured, ValidationError
from django.shortcuts import redirect, render, get_object_or_404
from django.views import View
from django.views.generic.edit import FormView, UpdateView
from django.urls import reverse
from tutorials.forms import (
    LogInForm, PasswordForm, UserForm, SignUpForm,
    TutorProfileForm, BookingForm, AdminBookingForm, TutorAvailablityForm
)
from tutorials.helpers import login_prohibited
from django.http import HttpResponseForbidden, HttpResponseBadRequest
from .models import User, Booking, Tutor, Language, Term, Lesson, Specialization
from django.contrib.admin.views.decorators import staff_member_required
from django.http import JsonResponse
from .models import Booking
from django.contrib.auth.decorators import login_required
from django.utils.timezone import now
import datetime
import logging
from django.views.decorators.http import require_http_methods

# Initialize logger
logger = logging.getLogger(__name__)

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
        """Returns the url to redirect to when logged in."""
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


# Handle the creation of a booking with a tutor.
@login_required
def create_booking(request):
    """Allow students to create a booking without selecting a tutor."""
    if request.method == 'POST':
        form = BookingForm(request.POST)
        if form.is_valid():
            try:
                booking = form.save(commit=False)
                booking.student = request.user
                # Optionally, set tutor to None explicitly
                booking.tutor = None
                booking.save()
                messages.success(request, "Booking created successfully! Awaiting tutor assignment.")
                return redirect('dashboard')
            except ValidationError as e:
                form.add_error(None, e)
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = BookingForm()

    return render(request, 'create_booking.html', {'form': form})


# Pending booking views
@staff_member_required
def pending_bookings(request):
    """Display all pending bookings for admin users."""
    bookings = Booking.objects.filter(status=Booking.PENDING).order_by('term__start_date')
    return render(request, 'admin_pending_bookings.html', {'bookings': bookings})


# Approve booking (Admin)
@staff_member_required
def approve_booking(request, booking_id):
    """Approve a specific booking and redirect to booking creation page."""
    logger.debug(f"Attempting to approve booking with ID: {booking_id}")
    
    booking = get_object_or_404(Booking, id=booking_id, status=Booking.PENDING)
    booking.status = Booking.ACCEPTED
    booking.save()
    logger.debug(f"Booking ID {booking_id} status updated to ACCEPTED.")
    
    messages.success(request, f"Booking with ID {booking_id} has been approved.")
    
    # Redirect to the admin booking creation page with booking_id as a GET parameter
    return redirect(reverse('admin_create_booking') + f'?booking_id={booking_id}')


# Reject booking (Admin)
@staff_member_required
def decline_booking(request, booking_id):
    """Decline a specific booking by rejecting student approval."""
    booking = get_object_or_404(Booking, id=booking_id, status=Booking.PENDING)
    
    # Set student approval to rejected
    booking.student_approval = Booking.STUDENT_REJECTED
    booking.save()
    
    messages.success(request, f"Booking with ID {booking_id} has been declined.")
    return redirect('admin_pending_bookings')


# Update booking status (Admin)
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


@login_required
def tutor_profile(request):
    """Allow tutors to select the languages and specializations they can teach."""
    user = request.user

    # Check if the user is a tutor
    if user.account_type != 'tutor':
        messages.error(request, "You must be a tutor to access this page.")
        return redirect('dashboard')

    # Ensure the Tutor object exists
    tutor, created = Tutor.objects.get_or_create(user=user)

    if request.method == 'POST':
        form = TutorProfileForm(request.POST, instance=tutor)
        if form.is_valid():
            form.save()
            messages.success(request, "Your teaching profile has been updated.")
            return redirect('tutor_availability')
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = TutorProfileForm(instance=tutor)

    return render(request, 'tutor_profile.html', {'form': form})
@require_http_methods(['GET', 'POST'])
def tutor_availability(request):
    """Allow tutors to select their availability."""
    if request.method == 'POST':
        form = TutorAvailablityForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Your availability has been updated.")
            return redirect('dashboard')
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = TutorAvailablityForm()

    return render(request, 'tutor_profile_availability.html', {'form': form})
@staff_member_required
def admin_create_booking(request):
    """Allow admins to create a new booking or edit an existing one."""
    booking_id = request.GET.get('booking_id')
    if booking_id:
        # Editing an existing booking
        booking = get_object_or_404(Booking, id=booking_id)
        if request.method == 'POST':
            form = AdminBookingForm(request.POST, instance=booking)
            if form.is_valid():
                booking = form.save(commit=False)
                # Optionally, set or update additional fields here
                booking.save()
                messages.success(request, f"Booking ID {booking.id} has been updated successfully.")
                return redirect('admin_pending_bookings')
            else:
                messages.error(request, "Please correct the errors below.")
        else:
            form = AdminBookingForm(instance=booking)
    else:
        # Creating a new booking
        if request.method == 'POST':
            form = AdminBookingForm(request.POST)
            if form.is_valid():
                booking = form.save(commit=False)
                booking.status = Booking.PENDING  # Booking is pending admin approval
                booking.student_approval = Booking.STUDENT_APPROVAL_PENDING  # Mark as pending student approval
                booking.tutor_approval = Booking.TUTOR_APPROVAL_PENDING  # Mark as pending tutor approval
                booking.save()
                messages.success(request, "Booking created successfully! Awaiting student and tutor approval.")
                return redirect('admin_pending_bookings')
            else:
                messages.error(request, "Please correct the errors below.")
        else:
            form = AdminBookingForm()
    
    context = {
        'form': form,
        'booking_id': booking_id if booking_id else None,
    }
    return render(request, 'admin_create_booking.html', context)


@login_required
def view_bookings(request):
    """Display bookings relevant to the logged-in user based on their account type."""
    user = request.user
    context = {}

    if user.account_type == 'student':
        # Fetch bookings where the user is the student
        student_bookings = Booking.objects.filter(student=user).order_by('term__start_date', 'day_of_week', 'start_time')
        context['student_bookings'] = student_bookings
        context['role'] = 'Student'
    elif user.is_tutor:
        try:
            tutor = user.tutor  # Access the related Tutor object
            tutor_bookings = Booking.objects.filter(tutor=tutor).order_by('term__start_date', 'day_of_week', 'start_time')
            context['tutor_bookings'] = tutor_bookings
            context['role'] = 'Tutor'
        except Tutor.DoesNotExist:
            messages.error(request, "Tutor profile does not exist. Please complete your tutor profile.")
            return redirect('tutor_profile')
    else:
        # Handle unexpected account types or non-student/tutor users
        messages.error(request, "You do not have access to this page.")
        return redirect('dashboard')

    return render(request, 'view_bookings.html', context)


# New Views to Handle Accepting and Rejecting Bookings by Students and Tutors
@login_required
def accept_booking(request, booking_id):
    """Allow students or tutors to accept a booking."""
    booking = get_object_or_404(Booking, id=booking_id)
    user = request.user

    # Check if the user is the student
    if booking.student == user:
        if booking.student_approval != Booking.STUDENT_APPROVED:
            booking.student_approval = Booking.STUDENT_APPROVED
            booking.save()
            messages.success(request, "You have accepted the booking.")
        else:
            messages.info(request, "You have already accepted this booking.")
    # Check if the user is the tutor
    elif hasattr(user, 'tutor') and booking.tutor == user.tutor:
        if booking.tutor_approval != Booking.TUTOR_APPROVED:
            booking.tutor_approval = Booking.TUTOR_APPROVED
            booking.save()
            messages.success(request, "You have accepted the booking.")
        else:
            messages.info(request, "You have already accepted this booking.")
    else:
        return HttpResponseForbidden("You are not allowed to perform this action.")

    return redirect('view_bookings')


@login_required
def reject_booking(request, booking_id):
    """Allow students or tutors to reject a booking."""
    booking = get_object_or_404(Booking, id=booking_id)
    user = request.user

    # Check if the user is the student
    if booking.student == user:
        if booking.student_approval != Booking.STUDENT_REJECTED:
            booking.student_approval = Booking.STUDENT_REJECTED
            booking.save()
            messages.success(request, "You have rejected the booking.")
        else:
            messages.info(request, "You have already rejected this booking.")
    # Check if the user is the tutor
    elif hasattr(user, 'tutor') and booking.tutor == user.tutor:
        if booking.tutor_approval != Booking.TUTOR_REJECTED:
            booking.tutor_approval = Booking.TUTOR_REJECTED
            booking.save()
            messages.success(request, "You have rejected the booking.")
        else:
            messages.info(request, "You have already rejected this booking.")
    else:
        return HttpResponseForbidden("You are not allowed to perform this action.")

    return redirect('view_bookings')

@login_required
def booking_calendar_data(request):
    user = request.user
    # Fetch bookings based on user type (student or tutor)
    if user.account_type == 'student':
        bookings = Booking.objects.filter(student=user)
    elif user.account_type == 'tutor':
        bookings = Booking.objects.filter(tutor=user)
    else:
        bookings = Booking.objects.none()

    events = []
    for booking in bookings:
        events.append({
            'title': f"{booking.student} - {booking.tutor}",
            'start': booking.date.isoformat(),
            'end': (booking.date + booking.duration).isoformat(),  # Assuming duration is timedelta
            'description': booking.description,
        })
    
    return JsonResponse(events, safe=False)


# Custom error handlers
def custom_404_view(request, exception):
    return render(request, '404.html', status=404)

def custom_500_view(request):
    return render(request, '500.html', status=500)

logger = logging.getLogger(__name__)

@login_required
def calendar_bookings_api(request):
    user = request.user
    logger.debug(f"Fetching calendar data for user: {user}")

    # Filter approved bookings for the current user
    if user.account_type == 'student':
        bookings = Booking.objects.filter(student=user, status=Booking.ACCEPTED)
    elif user.account_type == 'tutor':
        bookings = Booking.objects.filter(tutor=user.tutor, status=Booking.ACCEPTED)
    else:
        bookings = Booking.objects.none()

    events = []

    # Iterate over bookings to create events for recurring days
    for booking in bookings:
        # Ensure `day_of_week` matches valid days
        recurring_days = [booking.day_of_week]
        start_date = booking.term.start_date
        end_date = booking.term.end_date

        # Loop through all dates from start_date to end_date
        current_date = start_date
        while current_date <= end_date:
            # Check if the day of the week matches any recurring day
            if current_date.strftime('%A') in recurring_days:
                events.append({
                    'title': f"{booking.language.name} with {booking.tutor.user.full_name() if booking.tutor else 'No Tutor'}",
                    'date': current_date.isoformat(),  # Format as YYYY-MM-DD
                    'description': f"Subject: {booking.specialization.name if booking.specialization else 'General'}",
                })
            current_date += datetime.timedelta(days=1)

    return JsonResponse(events, safe=False)