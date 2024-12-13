from django.core.management.base import BaseCommand, CommandError
from tutorials.models import User, Term, Tutor, Language, Specialization, Booking, TutorAvalibility
from django.core.exceptions import ValidationError
import pytz
from faker import Faker
from random import randint, random
from datetime import datetime, timedelta, time


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
        self.create_admin_accounts()
        self.seed_tutor_availability()
        self.create_bookings()
        
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
    #user creation
    def create_user(self, data):
        User.objects.create_user(
            username=data['username'],
            email=data['email'],
            password=Command.DEFAULT_PASSWORD,
            first_name=data['first_name'],
            last_name=data['last_name'],
        )

    def create_admin_accounts(self):
        """Create 10 admin accounts."""
        admin_fixtures = [
            {'username': f'@admin{i}', 'email': f'admin{i}_{randint(100, 999)}@example.org', 'first_name': f'Admin{i}', 'last_name': 'User'}
            for i in range(1, 11)  # Generate 10 admin accounts
        ]

        for admin_data in admin_fixtures:
            try:
                user, created = User.objects.get_or_create(
                    username=admin_data['username'],
                    email=admin_data['email'],
                    defaults={
                        'first_name': admin_data['first_name'],
                        'last_name': admin_data['last_name'],
                    }
                )
                if created:
                    user.set_password(self.DEFAULT_PASSWORD)
                    user.is_staff = True
                    user.is_superuser = True
                    user.save()
                    self.stdout.write(self.style.SUCCESS(f"Created admin: {user.username}"))
                else:
                    self.stdout.write(f"Admin already exists: {user.username}")
            except Exception as e:
                self.stderr.write(f"Error creating admin {admin_data['username']}: {e}")

    #term creation
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

            term, created = Term.objects.get_or_create(
                name=term_data["name"],
                defaults={"start_date": start_date, "end_date": end_date}
            )

            if created:
                self.stdout.write(f"Created term: {term.name}")
            else:
                self.stdout.write(f"Term already exists: {term.name}")

    #language creation
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
        TUTOR_COUNT = 100  
        existing_tutors = Tutor.objects.count()

        while existing_tutors < TUTOR_COUNT:
            print(f"Seeding tutor {existing_tutors}/{TUTOR_COUNT}", end='\r')
            first_name = self.faker.first_name()
            last_name = self.faker.last_name()
            username = create_username(first_name, last_name)
            email = create_email(first_name, last_name)

            try:
                user, created = User.objects.get_or_create(
                    username=username,
                    email=email,
                    defaults={
                        'first_name': first_name,
                        'last_name': last_name,
                    }
                )
                if created:
                    user.set_password(self.DEFAULT_PASSWORD)
                    user.save()
                    self.stdout.write(self.style.SUCCESS(f"Added user for tutor: {user.username}"))

                tutor, created = Tutor.objects.get_or_create(user=user)
                if created:
                    languages = Language.objects.order_by('?')[:3]  
                    specializations = Specialization.objects.order_by('?')[:2]  
                    tutor.languages.set(languages)
                    tutor.specializations.set(specializations)
                    tutor.save()
                    self.stdout.write(self.style.SUCCESS(f"Added tutor: {user.username}"))

            except Exception as e:
                self.stderr.write(f"Error creating tutor: {e}")
                continue

            existing_tutors = Tutor.objects.count()
        print("Tutor seeding complete.")


    def create_bookings(self):
        """Create sample bookings for seeded data."""
        terms = Term.objects.all()
        languages = Language.objects.all()
        specializations = Specialization.objects.all()
        tutors = Tutor.objects.all()
        students = User.objects.filter(account_type='student')

        if not terms.exists() or not languages.exists() or not tutors.exists():
            self.stdout.write(self.style.WARNING("Insufficient data to create bookings. Seed terms, languages, and tutors first."))
            return

        for i in range(10):  
            student = students.order_by('?').first()
            language = languages.order_by('?').first()
            specialization = specializations.order_by('?').first() if random() > 0.5 else None

            if specialization:
                eligible_tutors = tutors.filter(specializations=specialization)
            else:
                eligible_tutors = tutors

            
            days_of_week = [choice[0] for choice in Booking.DAYS_OF_WEEK]
            day_of_week = self.faker.random_element(days_of_week)
            term = terms.order_by('?').first()

            available_tutors = eligible_tutors.filter(
                availabilities__term=term,
                availabilities__day_of_week__icontains=day_of_week
            ).distinct()

            
            if not available_tutors.exists():
                for retry_day in days_of_week:
                    if retry_day != day_of_week:
                        available_tutors = eligible_tutors.filter(
                            availabilities__term=term,
                            availabilities__day_of_week__icontains=retry_day
                        ).distinct()
                        if available_tutors.exists():
                            day_of_week = retry_day
                            break
                else:
                    
                    for retry_term in terms:
                        available_tutors = eligible_tutors.filter(
                            availabilities__term=retry_term,
                            availabilities__day_of_week__icontains=day_of_week
                        ).distinct()
                        if available_tutors.exists():
                            term = retry_term
                            break
                    else:
                        self.stderr.write(f"Skipping booking: No tutors available for term {term.name}.")
                        continue

            tutor = available_tutors.order_by('?').first()

           
            start_time = self.faker.time_object()
            duration = timedelta(hours=self.faker.random_int(min=1, max=3))
            frequency = self.faker.random_element([Booking.WEEKLY, Booking.FORTNIGHTLY])
            experience_level = self.faker.text(max_nb_chars=100)

            booking = Booking(
                student=student,
                tutor=tutor,
                language=language,
                term=term,
                specialization=specialization,
                day_of_week=day_of_week,
                start_time=start_time,
                duration=duration,
                frequency=frequency,
                experience_level=experience_level,
                student_approval=Booking.STUDENT_APPROVED if random() > 0.5 else Booking.STUDENT_APPROVAL_PENDING,
                tutor_approval=Booking.TUTOR_APPROVED if random() > 0.5 else Booking.TUTOR_APPROVAL_PENDING,
            )

            try:
                booking.full_clean()
                booking.save()
                self.stdout.write(self.style.SUCCESS(f"Created booking: {booking}"))
            except ValidationError as e:
                self.stderr.write(f"Error creating booking: {e}")

    def seed_tutor_availability(self):
        terms = Term.objects.all()
        tutors = Tutor.objects.all()
    
        for tutor in tutors:
            for term in terms:
               
                for day in ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']:
                    TutorAvalibility.objects.get_or_create(
                        tutor=tutor,
                        term=term,
                        day_of_week=day,
                        start_time=time(9, 0), 
                        end_time=time(17, 0)   
                    )


def create_username(first_name, last_name):
    return '@' + first_name.lower() + last_name.lower()

def create_email(first_name, last_name):
    return first_name + '.' + last_name + '@example.org'
