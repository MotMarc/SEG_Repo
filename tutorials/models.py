from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.db import models
from libgravatar import Gravatar
#...
from django.contrib.auth import get_user_model



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

#booking

class Language(models.Model):
    """Represents a programming language that tutors can teach."""
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name

# Define the Tutor model
class Tutor(models.Model):
    """Represents a tutor, extending the user with additional information."""
    user = models.OneToOneField('User', on_delete=models.CASCADE)  # Use string reference
    languages = models.ManyToManyField('Language', related_name='tutors')  # Use string reference

    def __str__(self):
        return f'Tutor: {self.user.full_name()}'

# Define booking for a language.
class Booking(models.Model):
    

    PENDING = 'Pending'
    ACCEPTED = 'Accepted'
    DECLINED = 'Declined'

    STATUS_CHOICES = [
        (PENDING, 'Pending'),
        (ACCEPTED, 'Accepted'),
        (DECLINED, 'Declined'),
    ]

    student = models.ForeignKey('User', on_delete=models.CASCADE, related_name='student_bookings')  # Use string reference
    tutor = models.ForeignKey('Tutor', on_delete=models.CASCADE, related_name='tutor_bookings')  # Use string reference
    language = models.ForeignKey('Language', on_delete=models.CASCADE)  # Use string reference
    booking_time = models.DateTimeField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default=PENDING)

    def __str__(self):
        return (
            f"Booking by {self.student.username} with {self.tutor.user.username} "
            f"for {self.language.name} at {self.booking_time} (Status: {self.status})"
        )  
    
class Invoice(models.Model):

    booking = models.ForeignKey('Booking', on_delete = models.CASCADE)
    amount = models.DecimalField(max_digits = 10, decimal_places = 2, blank = True, null = True)
    is_paid = models.BooleanField(default = False)

    def save(self, *args, **kwargs):
        if self.booking:
            tutor = self.booking.tutor
            student = self.booking.student
            self.amount = 0
        super().save(*args, **kwargs)