from django.core.management.base import BaseCommand, CommandError

from tutorials.models import User, Term, Tutor, Language, Specialization

import pytz
from faker import Faker
from random import randint, random
from datetime import datetime


user_fixtures = [
    {'username': '@johndoe', 'email': 'john.doe@example.org', 'first_name': 'John', 'last_name': 'Doe'},
    {'username': '@janedoe', 'email': 'jane.doe@example.org', 'first_name': 'Jane', 'last_name': 'Doe'},
    {'username': '@charlie', 'email': 'charlie.johnson@example.org', 'first_name': 'Charlie', 'last_name': 'Johnson'},
]

language_fixtures = [
    'Python',
    'JavaScript',
    'Ruby',
    'Java',
    'C++',
    'HTML',
    'CSS',
     'C', 'Golang', 'SQL', 'Kotlin', 'Rust', 'PHP', 'R', 'Dart', 'Django', 'C#', 'Swift', 'Perl', 'Scala', 'Haskell'
]

tutor_fixtures = [
    {'username': '@tutoralice', 'email': 'alice.tutor@example.org', 'first_name': 'Alice', 'last_name': 'Tutor'},
    {'username': '@tutorbob', 'email': 'bob.tutor@example.org', 'first_name': 'Bob', 'last_name': 'Tutor'},
]


SPECIALIZATION_LANGUAGE_MAP = {
    'Data Structure': ['C', 'C++', 'Java', 'Python', 'Rust', 'Haskell', 'Scala'],
    'Web Development': ['HTML', 'Django', 'Golang', 'Perl', 'Scala','CSS', 'Python', 'JavaScript', 'Ruby', 'PHP', 'Java', 'C#', 'Swift'],
    'Machine Learning': ['Python', 'R', 'Java', 'C++', 'Scala', 'Haskell'],
    'Cybersecurity': ['Python', 'C', 'C++', 'Java', 'JavaScript', 'Rust', 'Golang', 'Perl'],
    'Cloud Computing': ['Python', 'Java', 'Golang', 'Ruby', 'C#', 'Kotlin', 'Rust', 'Scala'],
    'Game Development': ['C++', 'C#', 'JavaScript', 'Java', 'Python', 'Swift', 'Golang'],
    'Robotics': ['C++', 'Python', 'Java', 'C', 'Rust'],
    'Mobile App Development': ['Java', 'Kotlin', 'Swift', 'Dart', 'C#'],
    'UI/UX Design': ['HTML', 'CSS', 'JavaScript', 'Swift', 'Dart'],
    'Database Administration': ['SQL', 'Python', 'PHP', 'Java', 'C#', 'Perl'],
}

class Command(BaseCommand):
    """Build automation command to seed the database."""

    USER_COUNT = 300
    DEFAULT_PASSWORD = 'Password123'
    help = 'Seeds the database with sample data'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.faker = Faker('en_GB')

    def handle(self, *args, **options):
        self.create_users()
        self.create_terms()
        self.create_languages()
        self.create_specializations()
        self.create_tutors()

    def create_users(self):
        self.generate_user_fixtures()
        self.generate_random_users()

    def generate_user_fixtures(self):
        for data in user_fixtures:
            self.try_create_user(data)

    def generate_random_users(self):
        user_count = User.objects.count()
        while  user_count < self.USER_COUNT:
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

    def create_terms(self):
        """Seed the database with academic terms."""
        term_fixtures = [
            {"name": "September-Christmas", "start_date": "2024-09-01", "end_date": "2024-12-20"},
            {"name": "January-Easter", "start_date": "2025-01-10", "end_date": "2025-04-10"},
            {"name": "May-July", "start_date": "2025-05-01", "end_date": "2025-07-20"},
        ]

        for term_data in term_fixtures:
            start_date = datetime.strptime(term_data["start_date"], "%Y-%m-%d").date()
            end_date = datetime.strptime(term_data["end_date"], "%Y-%m-%d").date()

            if start_date >= end_date:
                self.stderr.write(f"Invalid term dates: {term_data['name']}. Start date must be before end date.")
                continue

            # Create term if it doesn't exist
            term, created = Term.objects.get_or_create(
                name=term_data["name"],
                defaults={"start_date": start_date, "end_date": end_date}
            )

            if created:
                self.stdout.write(f"Created term: {term.name}")
            else:
                self.stdout.write(f"Term already exists: {term.name}")


    def create_languages(self):
        """Seed languages into the database."""
        for language in language_fixtures:
            _, created = Language.objects.get_or_create(name=language)
            if created:
                self.stdout.write(self.style.SUCCESS(f"Added language: {language}"))

    def create_specializations(self):
        """Seed specializations into the database and link them to applicable languages."""
        for specialization in SPECIALIZATION_LANGUAGE_MAP:
            spec, created = Specialization.objects.get_or_create(name=specialization)
            if created:
                self.stdout.write(self.style.SUCCESS(f"Added specialization: {specialization}"))
            
            # Link specialization to languages based on the predefined map
            applicable_languages = SPECIALIZATION_LANGUAGE_MAP.get(specialization, [])
            for lang_name in applicable_languages:
                try:
                    language = Language.objects.get(name=lang_name)
                    spec.languages.add(language)
                    self.stdout.write(self.style.SUCCESS(f"Linked {specialization} to {lang_name}"))
                except Language.DoesNotExist:
                    self.stderr.write(f"Language '{lang_name}' does not exist. Cannot link to specialization '{specialization}'.")
            
            spec.save()
    def create_tutors(self):
        """Seed tutors into the database."""
        for tutor_data in tutor_fixtures:
            user, created = User.objects.get_or_create(
                username=tutor_data['username'],
                email=tutor_data['email'],
                defaults={
                    'first_name': tutor_data['first_name'],
                    'last_name': tutor_data['last_name'],
                }
            )
            if created:
                # Set password separately to ensure it's hashed
                user.set_password(self.DEFAULT_PASSWORD)
                user.save()
                self.stdout.write(self.style.SUCCESS(f"Added user for tutor: {user.username}"))

            tutor, created = Tutor.objects.get_or_create(user=user)
            if created:
                # Assign random languages and specializations
                languages = Language.objects.order_by('?')[:3]
                specializations = Specialization.objects.order_by('?')[:2]
                tutor.languages.set(languages)
                tutor.specializations.set(specializations)
                tutor.save()
                self.stdout.write(self.style.SUCCESS(f"Added tutor: {user.username}"))



def create_username(first_name, last_name):
    return '@' + first_name.lower() + last_name.lower()

def create_email(first_name, last_name):
    return first_name + '.' + last_name + '@example.org'


