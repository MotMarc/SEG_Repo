from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.db import models
from libgravatar import Gravatar


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


class UserProfile(models.Model):
    """Model for additional user profile information and roles."""

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    role = models.CharField(
        max_length=20,
        choices=[
            ('admin', 'Admin'),
            ('tutor', 'Tutor'),
            ('student', 'Student'),
        ]
    )

    def __str__(self):
        return f"{self.user.username} - {self.role}"


class LessonRequest(models.Model):
    """Model to handle lesson requests submitted by students."""

    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name="lesson_requests")
    subject = models.CharField(max_length=100)
    description = models.TextField()
    status = models.CharField(
        max_length=20,
        choices=[
            ('pending', 'Pending'),
            ('approved', 'Approved'),
            ('rejected', 'Rejected'),
        ],
        default='pending'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.subject} - {self.student.username}"


class Lesson(models.Model):
    """Model for scheduled lessons."""

    request = models.OneToOneField(LessonRequest, on_delete=models.CASCADE, related_name="lesson")
    tutor = models.ForeignKey(User, on_delete=models.CASCADE, related_name="lessons")
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()

    def __str__(self):
        return f"{self.request.subject} - {self.tutor.username}"


class Invoice(models.Model):
    """Model to handle lesson invoices."""

    lesson = models.OneToOneField(Lesson, on_delete=models.CASCADE, related_name="invoice")
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    is_paid = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Invoice for {self.lesson.request.subject} - Paid: {self.is_paid}"
