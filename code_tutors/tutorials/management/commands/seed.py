from django.core.management.base import BaseCommand
from tutorials.models import User, UserProfile, LessonRequest, Lesson, Invoice
import pytz
from faker import Faker
from random import choice
from datetime import timedelta  # Import timedelta for duration calculations

user_fixtures = [
    {'username': '@johndoe', 'email': 'john.doe@example.org', 'first_name': 'John', 'last_name': 'Doe'},
    {'username': '@janedoe', 'email': 'jane.doe@example.org', 'first_name': 'Jane', 'last_name': 'Doe'},
    {'username': '@charlie', 'email': 'charlie.johnson@example.org', 'first_name': 'Charlie', 'last_name': 'Johnson'},
]


class Command(BaseCommand):
    """Build automation command to seed the database."""

    USER_COUNT = 300
    DEFAULT_PASSWORD = 'Password123'
    DEFAULT_ROLE = 'student'
    DEFAULT_SUBJECTS = ['Math', 'English', 'Science']
    DEFAULT_LESSON_DURATION = 1  # in hours
    DEFAULT_INVOICE_AMOUNT = 50.0
    help = 'Seeds the database with sample data'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.faker = Faker('en_GB')

    def handle(self, *args, **options):
        self.create_users()
        self.users = User.objects.all()
        self.create_roles_and_profiles()
        self.create_lesson_requests()
        self.create_lessons_and_invoices()

    def create_users(self):
        self.generate_user_fixtures()
        self.generate_random_users()

    def generate_user_fixtures(self):
        for data in user_fixtures:
            self.try_create_user(data)

    def generate_random_users(self):
        user_count = User.objects.count()
        while user_count < self.USER_COUNT:
            print(f"Seeding user {user_count}/{self.USER_COUNT}", end='\r')
            self.generate_user()
            user_count = User.objects.count()
        print("User seeding complete.      ")

    def generate_user(self):
        first_name = self.faker.first_name()
        last_name = self.faker.last_name()
        email = create_email(first_name, last_name)
        username = create_username(first_name, last_name)
        self.try_create_user({'username': username, 'email': email, 'first_name': first_name, 'last_name': last_name})

    def try_create_user(self, data):
        try:
            self.create_user(data)
        except:
            pass

    def create_user(self, data):
        User.objects.create_user(
            username=data['username'],
            email=data['email'],
            password=Command.DEFAULT_PASSWORD,
            first_name=data['first_name'],
            last_name=data['last_name'],
        )

    def create_roles_and_profiles(self):
        """Assign roles to all users."""
        print("Assigning roles to users...")
        for user in self.users:
            # Check if the user already has a profile
            if not UserProfile.objects.filter(user=user).exists():
                role = choice(['admin', 'tutor', 'student'])
                UserProfile.objects.create(user=user, role=role)
        print("Roles assigned.")

    def create_lesson_requests(self):
        """Create lesson requests for students."""
        print("Creating lesson requests...")
        students = UserProfile.objects.filter(role='student').select_related('user')
        for student_profile in students[:20]:  # Limit to 20 students for demonstration
            subject = choice(Command.DEFAULT_SUBJECTS)
            description = self.faker.text(max_nb_chars=100)
            LessonRequest.objects.create(
                student=student_profile.user,
                subject=subject,
                description=description,
            )
        print("Lesson requests created.")

    def create_lessons_and_invoices(self):
        """Create lessons and invoices for approved requests."""
        print("Creating lessons and invoices...")
        tutors = UserProfile.objects.filter(role='tutor').select_related('user')
        requests = LessonRequest.objects.all()

        for lesson_request in requests:
            if tutors.exists():
                tutor = choice(tutors).user
                start_time = self.faker.date_time_this_month(tzinfo=pytz.UTC)
                end_time = start_time + timedelta(hours=Command.DEFAULT_LESSON_DURATION)  # Fixed timedelta usage
                lesson = Lesson.objects.create(
                    request=lesson_request,
                    tutor=tutor,
                    start_time=start_time,
                    end_time=end_time,
                )
                Invoice.objects.create(
                    lesson=lesson,
                    amount=Command.DEFAULT_INVOICE_AMOUNT,
                    is_paid=choice([True, False]),
                )
        print("Lessons and invoices created.")


def create_username(first_name, last_name):
    return '@' + first_name.lower() + last_name.lower()


def create_email(first_name, last_name):
    return first_name.lower() + '.' + last_name.lower() + '@example.org'
