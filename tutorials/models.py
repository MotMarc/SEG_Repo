from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.db import models
from libgravatar import Gravatar
#...
from django.contrib.auth import get_user_model
from datetime import timedelta, time



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

    # Frequency Choices
    WEEKLY = 'Weekly'
    FORTNIGHTLY = 'Fortnightly'
    FREQUENCY_CHOICES = [
        (WEEKLY, 'Weekly'),
        (FORTNIGHTLY, 'Fortnightly'),
    ]

    student = models.ForeignKey(
        'User',
        on_delete=models.CASCADE,
        related_name='bookings_as_student',
        verbose_name='Student'
    )
    tutor = models.ForeignKey(
        'Tutor',
        on_delete=models.CASCADE,
        related_name='bookings_as_tutor',
        verbose_name='Tutor'
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

    start_time = models.TimeField(verbose_name='Start Time', null=False, blank=False, default=time(10, 0))

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

    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default=PENDING)

    day_of_week = models.CharField(
        max_length=15,
        choices=DAYS_OF_WEEK,
        default="Monday",  # Ensure a default
        verbose_name="Day of the Week"
    )
    term = models.ForeignKey('Term', on_delete=models.CASCADE)

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

    def __str__(self):
        return f'Booking {self.id}: {self.student.full_name()} with {self.tutor.user.full_name()} for {self.language.name}'

#...
class Term(models.Model):
    name = models.CharField(max_length=50)
    start_date = models.DateField()
    end_date = models.DateField()

    def __str__(self):
        return self.name

class Lesson(models.Model):
    booking = models.ForeignKey('Booking', on_delete=models.CASCADE)
    date = models.DateField()
    start_time = models.TimeField()
    duration = models.DurationField()

    def __str__(self):
        return f'Lesson on {self.date} at {self.start_time}'