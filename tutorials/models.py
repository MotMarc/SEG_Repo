from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.db import models
from libgravatar import Gravatar
#...
from django.contrib.auth import get_user_model
from datetime import timedelta, time
from django.core.exceptions import ValidationError




class User(AbstractUser):
    """Model used for user authentication, and team member-related information."""

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

#Define tutor
    @property
    def is_tutor(self):
        return hasattr(self, 'tutor')
    
#booking

class Language(models.Model):
    """Represents a programming language that tutors can teach."""
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name

# Define the Tutor model
class Tutor(models.Model):
    """Represents a tutor, extending the user with additional information."""
    user = models.OneToOneField('User', on_delete=models.CASCADE)
    languages = models.ManyToManyField('Language', related_name='tutors')
    specializations = models.ManyToManyField('Specialization', related_name='specialized_tutors', blank=True)

    def __str__(self):
        return f'Tutor: {self.user.full_name()}'


# Define booking for a language.
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

    tutor = models.ForeignKey(
    'Tutor',
    on_delete=models.CASCADE,
    related_name='bookings',
    verbose_name='Tutor',
    null=True  # Allow null values temporarily
    )

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

    start_time = models.TimeField(
        verbose_name='Start Time', 
        null=False, blank=False, 
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
        default="Monday",  # Ensure a default
        verbose_name="Day of the Week"
    )

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
        """Validate that the booking's date is within the term and does not overlap."""
        # Ensure the booking's day of the week aligns with the term's date range
        term_start = self.term.start_date
        term_end = self.term.end_date
        booking_date = self.calculate_booking_date(term_start)

        if booking_date < term_start or booking_date > term_end:
            raise ValidationError(f"Booking date {booking_date} must fall within the term dates {term_start} to {term_end}.")

        # Validate no overlapping bookings for the same tutor
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

    def __str__(self):
        return f'Booking {self.id}: {self.student.full_name()} with {self.tutor.user.full_name()} for {self.language.name}'

#...


class Lesson(models.Model):
    booking = models.ForeignKey('Booking', on_delete=models.CASCADE)
    date = models.DateField()
    start_time = models.TimeField()
    duration = models.DurationField()

    def __str__(self):
        return f'Lesson on {self.date} at {self.start_time}'
    
#....
class Specialization(models.Model):
    """Represents an advanced specialization that tutors can teach."""
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name
    

class Term(models.Model):
    """Represents an academic term."""
    name = models.CharField(max_length=50)
    start_date = models.DateField()
    end_date = models.DateField()

    def clean(self):
        """Validate term dates to follow the London State School Calendar."""
        if "September" in self.name and not (9 <= self.start_date.month <= 12):
            raise ValidationError("September-Christmas term must start between September and December.")
        if "January" in self.name and not (1 <= self.start_date.month <= 4):
            raise ValidationError("January-Easter term must start between January and April.")
        if "May" in self.name and not (5 <= self.start_date.month <= 7):
            raise ValidationError("May-July term must start between May and July.")

        if self.start_date >= self.end_date:
            raise ValidationError("Term start date must be before the end date.")

    def __str__(self):
        return self.name
