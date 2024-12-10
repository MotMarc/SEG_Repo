from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.db import models
from libgravatar import Gravatar
from django.core.exceptions import ValidationError
from datetime import timedelta, time
from multiselectfield import MultiSelectField


class User(AbstractUser):
    """Model used for user authentication, and team member-related information."""

    ACCOUNT_TYPES = [
        ('student', 'Student'),
        ('tutor', 'Tutor'),
    ]

    username = models.CharField(
        max_length=30,
        unique=True,
        validators=[RegexValidator(
            regex=r'^@\w{3,}$',
            message='Username must consist of @ followed by at least three alphanumericals'
        )]
    )
    first_name = models.CharField(max_length=50, blank=False)
    last_name = models.CharField(max_length=50, blank=False)
    email = models.EmailField(unique=True, blank=False)
    account_type = models.CharField(
        max_length=10,
        choices=ACCOUNT_TYPES,
        default='student',
        blank=False
    )

    class Meta:
        """Model options."""
        ordering = ['last_name', 'first_name']

    def full_name(self):
        """Return a string containing the user's full name."""
        return f'{self.first_name} {self.last_name}'

    def gravatar(self, size=120):
        """Return a URL to the user's gravatar."""
        gravatar_object = Gravatar(self.email)
        gravatar_url = gravatar_object.get_image(size=size, default='mp')
        return gravatar_url

    def mini_gravatar(self):
        """Return a URL to a miniature version of the user's gravatar."""
        return self.gravatar(size=60)

    @property
    def is_tutor(self):
        """Check if the user is a tutor."""
        return self.account_type == 'tutor'


class Language(models.Model):
    """Represents a programming language that tutors can teach."""
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name


class Specialization(models.Model):
    """Represents an advanced specialization that tutors can teach."""
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


class Tutor(models.Model):
    """Represents a tutor, extending the user with additional information."""
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    languages = models.ManyToManyField('Language', related_name='tutors')
    specializations = models.ManyToManyField('Specialization', related_name='specialized_tutors', blank=True)

    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name}"


class Term(models.Model):
    # Define a limited set of choices for the term name
    TERM_CHOICES = [
        ('September-Christmas', 'September-Christmas'),
        ('January-Easter', 'January-Easter'),
        ('May-July', 'May-July'),
    ]

    # Use a CharField with predefined choices for the term name
    name = models.CharField(
        max_length=50,
        choices=TERM_CHOICES,
        help_text="Select the term from the given options."
    )
    start_date = models.DateField()
    end_date = models.DateField()

    def clean(self):
        """
        Validate the start_date and end_date based on the selected term name.
        Also ensure that the start_date is before the end_date.
        """
        # Validate date ranges according to the chosen term name
        if self.name == 'September-Christmas':
            # The start month should be between September(9) and December(12)
            if not (9 <= self.start_date.month <= 12):
                raise ValidationError("September-Christmas term must start between September and December.")

        elif self.name == 'January-Easter':
            # The start month should be between January(1) and April(4)
            if not (1 <= self.start_date.month <= 4):
                raise ValidationError("January-Easter term must start between January and April.")

        elif self.name == 'May-July':
            # The start month should be between May(5) and July(7)
            if not (5 <= self.start_date.month <= 7):
                raise ValidationError("May-July term must start between May and July.")

        # Ensure the start date is before the end date
        if self.start_date >= self.end_date:
            raise ValidationError("Term start date must be before the end date.")

    def __str__(self):
        # Return a string representation of the term
        return f"{self.name} ({self.start_date} - {self.end_date})"


class TutorAvalibility(models.Model):
    DAY_CHOICES = [
        ('monday', 'Monday'),
        ('tuesday', 'Tuesday'),
        ('wednesday', 'Wednesday'),
        ('thursday', 'Thursday'),
        ('friday', 'Friday'),
        ('saturday', 'Saturday'),
        ('sunday', 'Sunday'),
    ]

    """Represents a tutor's avalibility."""
    tutor = models.ForeignKey(Tutor, on_delete=models.CASCADE, related_name='availabilities')
    term = models.ForeignKey(Term, on_delete=models.CASCADE, related_name='availabilities',)
    day_of_week = MultiSelectField(choices=DAY_CHOICES)
    start_time = models.TimeField()
    end_time = models.TimeField()
    def clean(self):
        """Custom validation for time range."""
        allowed_start = time(hour=9, minute=0)
        allowed_end = time(hour=19, minute=0)

        if not (allowed_start <= self.start_time <= allowed_end):
            raise ValidationError(f"Start time must be between {allowed_start} and {allowed_end}.")
        if not (allowed_start <= self.end_time <= allowed_end):
            raise ValidationError(f"End time must be between {allowed_start} and {allowed_end}.")
        if self.start_time >= self.end_time:
            raise ValidationError("End time must be after start time.")

    def __str__(self):
        return f"{self.day_of_week}: {self.start_time}-{self.end_time}"

class BookingManager(models.Manager):
    """Custom manager for filtering bookings by student approval."""

    def pending_approval(self):
        return self.filter(student_approval=Booking.STUDENT_APPROVAL_PENDING)

    def approved(self):
        return self.filter(student_approval=Booking.STUDENT_APPROVED)

    def rejected(self):
        return self.filter(student_approval=Booking.STUDENT_REJECTED)


class Booking(models.Model):
    """Represents a booking for tutoring services."""

    # Status Choices
    PENDING = 'Pending'
    ACCEPTED = 'Accepted'
    DECLINED = 'Declined'
    STATUS_CHOICES = [
        (PENDING, 'Pending'),
        (ACCEPTED, 'Accepted'),
        (DECLINED, 'Declined'),
    ]

    # Student Approval Choices
    STUDENT_APPROVAL_PENDING = 'Pending'
    STUDENT_APPROVED = 'Approved'
    STUDENT_REJECTED = 'Rejected'
    STUDENT_APPROVAL_CHOICES = [
        (STUDENT_APPROVAL_PENDING, 'Pending Approval'),
        (STUDENT_APPROVED, 'Approved'),
        (STUDENT_REJECTED, 'Rejected'),
    ]

    # Tutor Approval Choices
    TUTOR_APPROVAL_PENDING = 'Pending'
    TUTOR_APPROVED = 'Approved'
    TUTOR_REJECTED = 'Rejected'
    TUTOR_APPROVAL_CHOICES = [
        (TUTOR_APPROVAL_PENDING, 'Pending Approval'),
        (TUTOR_APPROVED, 'Approved'),
        (TUTOR_REJECTED, 'Rejected'),
    ]

    tutor_approval = models.CharField(
        max_length=10,
        choices=TUTOR_APPROVAL_CHOICES,
        default=TUTOR_APPROVAL_PENDING,
        verbose_name='Tutor Approval'
    )

    DAYS_OF_WEEK = [
        ('Monday', 'Monday'),
        ('Tuesday', 'Tuesday'),
        ('Wednesday', 'Wednesday'),
        ('Thursday', 'Thursday'),
        ('Friday', 'Friday'),
        ('Saturday', 'Saturday'),
        ('Sunday', 'Sunday'),
    ]

    WEEKLY = 'Weekly'
    FORTNIGHTLY = 'Fortnightly'
    FREQUENCY_CHOICES = [
        (WEEKLY, 'Weekly'),
        (FORTNIGHTLY, 'Fortnightly'),
    ]

    tutor = models.ForeignKey(Tutor, related_name='tutor_bookings', on_delete=models.CASCADE, null=True, blank=True)
    specialization = models.ForeignKey(
        'Specialization',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='bookings',
        verbose_name='Specialization'
    )
    student = models.ForeignKey(
        'User',
        on_delete=models.CASCADE,
        related_name='bookings_as_student',
        verbose_name='Student'
    )
    language = models.ForeignKey(
        'Language',
        on_delete=models.CASCADE,
        related_name='bookings',
        verbose_name='Language'
    )
    term = models.ForeignKey(
        'Term',
        on_delete=models.CASCADE,
        related_name='bookings',
        verbose_name='Term'
    )
    frequency = models.CharField(
        max_length=15,
        choices=FREQUENCY_CHOICES,
        default=WEEKLY,
        verbose_name='Frequency'
    )
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default=PENDING,
        verbose_name='Status'
    )
    student_approval = models.CharField(
        max_length=10,
        choices=STUDENT_APPROVAL_CHOICES,
        default=STUDENT_APPROVAL_PENDING,
        verbose_name='Student Approval'
    )
    start_time = models.TimeField(
        verbose_name='Start Time',
        null=False,
        blank=False,
        default=time(10, 0)
    )
    duration = models.DurationField(
        help_text="Duration of each lesson (e.g., 1 hour)",
        verbose_name='Duration',
        default=timedelta(hours=1)
    )
    experience_level = models.TextField(
        verbose_name="Experience Level",
        max_length=500,
        blank=True,
        help_text="Describe your coding experience level in 100 words or less."
    )
    day_of_week = models.CharField(
        max_length=15,
        choices=DAYS_OF_WEEK,
        default="Monday",
        verbose_name="Day of the Week"
    )

    objects = BookingManager()  # Use custom manager

    class Meta:
        ordering = ['term__start_date', 'day_of_week', 'start_time']
        verbose_name = 'Booking'
        verbose_name_plural = 'Bookings'
        constraints = [
            models.UniqueConstraint(
                fields=['tutor', 'term', 'day_of_week', 'start_time'],
                condition=models.Q(status='Accepted'),
                name='unique_tutor_booking_per_time'
            )
        ]

    def clean(self):
        """Validate that the booking's fields are correct and consistent."""
        if not self.term_id:
            raise ValidationError({'term': 'Please select a term.'})

        if self.specialization and self.tutor:
            if not self.tutor.specializations.filter(id=self.specialization.id).exists():
                raise ValidationError({'specialization': f"The selected tutor does not offer specialization in {self.specialization}."})

        term_start = self.term.start_date
        term_end = self.term.end_date
        booking_date = self.calculate_booking_date(term_start)

        if booking_date < term_start or booking_date > term_end:
            raise ValidationError(f"Booking date {booking_date} must fall within the term dates {term_start} to {term_end}.")

        overlapping_bookings = Booking.objects.filter(
            tutor=self.tutor,
            term=self.term,
            day_of_week=self.day_of_week,
            start_time=self.start_time,
            status=Booking.ACCEPTED
        ).exclude(pk=self.pk)

        if overlapping_bookings.exists():
            raise ValidationError(f"Tutor is already booked at this time: {self.day_of_week} at {self.start_time}.")

    def calculate_booking_date(self, term_start):
        """Calculate the first occurrence of the booking's day of the week within the term."""
        term_start_weekday = term_start.weekday()
        booking_weekday = self.get_weekday_index(self.day_of_week)

        days_difference = (booking_weekday - term_start_weekday) % 7
        booking_date = term_start + timedelta(days=days_difference)
        return booking_date

    @staticmethod
    def get_weekday_index(day_name):
        """Convert weekday name to a numerical index (Monday=0, Sunday=6)."""
        days = {day: index for index, day in enumerate([
            'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'
        ])}
        return days[day_name]

    def get_recurring_dates(self):
        """Calculate all recurring dates for the booking."""
        if not self.term:
            return []

        recurring_dates = []
        current_date = self.term.start_date
        while current_date <= self.term.end_date:
            if current_date.strftime('%A') == self.day_of_week:
                recurring_dates.append(current_date)
            current_date += timedelta(days=1)

        return recurring_dates

    @classmethod
    def fetch_calendar_data(cls, user):
        """
        Fetch approved bookings for the given user and return data for the calendar.
        """
        if user.account_type == 'student':
            bookings = cls.objects.filter(student=user, status='Accepted')
        elif hasattr(user, 'tutor') and user.tutor:
            bookings = cls.objects.filter(tutor=user.tutor, status='Accepted')
        else:
            bookings = cls.objects.none()

        calendar_data = []
        for booking in bookings:
            recurring_dates = booking.get_recurring_dates()
            for date in recurring_dates:
                calendar_data.append({
                    'title': f"{booking.language.name if booking.language else 'No Language'} with {booking.tutor.user.full_name() if booking.tutor else 'No Tutor'}",
                    'date': date.isoformat(),
                    'description': f"Subject: {booking.specialization.name if booking.specialization else 'General'}",
                })

        return calendar_data

    def __str__(self):
        tutor_name = self.tutor.user.full_name() if self.tutor else "No Tutor Assigned"
        return f'Booking {self.id}: {self.student.full_name()} with {tutor_name} for {self.language.name}'

class Lesson(models.Model):
    """Represents a lesson generated from a booking."""
    booking = models.ForeignKey('Booking', on_delete=models.CASCADE)
    date = models.DateField()
    start_time = models.TimeField()
    duration = models.DurationField()

    def __str__(self):
        return f'Lesson on {self.date} at {self.start_time}'

