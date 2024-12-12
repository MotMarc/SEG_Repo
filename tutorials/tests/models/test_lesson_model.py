from django.test import TestCase
from datetime import date, time, timedelta
from tutorials.models import Lesson, Booking, Tutor, User, Term, Language

class LessonModelTests(TestCase):
    def setUp(self):
        """
        Set up initial data for the tests.
        """
        self.language = Language.objects.create(name="Python")
        self.user_student = User.objects.create(
            username="@studentexample",
            first_name="Alice",
            last_name="Wonder",
            email="alice@example.com",
            account_type="student"
        )
        self.user_tutor = User.objects.create(
            username="@tutorexample",
            first_name="John",
            last_name="Doe",
            email="john.doe@example.com",
            account_type="tutor"
        )
        self.tutor = Tutor.objects.create(user=self.user_tutor)
        self.term = Term.objects.create(
            name="May-July",
            start_date=date(2024, 5, 1),
            end_date=date(2024, 7, 31)
        )
        self.booking = Booking.objects.create(
            tutor=self.tutor,
            student=self.user_student,
            language=self.language,
            term=self.term,
            start_time=time(10, 0),
            day_of_week="Monday",
            duration=timedelta(hours=1)
        )

    def test_valid_lesson(self):
        """
        Test creating a valid Lesson.
        """
        lesson = Lesson.objects.create(
            booking=self.booking,
            date=date(2024, 5, 6),
            start_time=time(10, 0),
            duration=timedelta(hours=1)
        )
        self.assertEqual(str(lesson), "Lesson on 2024-05-06 at 10:00:00")
