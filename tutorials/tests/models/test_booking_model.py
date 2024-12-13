from django.test import TestCase
from datetime import date, time, timedelta
from tutorials.models import Booking, Tutor, User, Term, Language, TutorAvalibility

class BookingModelTests(TestCase):
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
        TutorAvalibility.objects.create(
            tutor=self.tutor,
            term=self.term,
            day_of_week=['monday'],
            start_time=time(10, 0),
            end_time=time(14, 0)
        )

    def test_valid_booking(self):
        """
        Test creating a valid booking.
        """
        booking = Booking.objects.create(
            tutor=self.tutor,
            student=self.user_student,
            language=self.language,
            term=self.term,
            start_time=time(10, 30),
            day_of_week="Monday",
            duration=timedelta(hours=1)
        )
        booking.clean()  
        self.assertEqual(str(booking), "Booking 1: Alice Wonder with John Doe for Python")

    def test_booking_outside_availability(self):
        """
        Test that booking outside tutor availability raises ValidationError.
        """
        booking = Booking(
            tutor=self.tutor,
            student=self.user_student,
            language=self.language,
            term=self.term,
            start_time=time(15, 0),  
            day_of_week="Monday",
            duration=timedelta(hours=1)
        )
        with self.assertRaises(Exception):
            booking.clean()

    def test_booking_overlap(self):
        """
        Test that overlapping bookings are rejected.
        """
        Booking.objects.create(
            tutor=self.tutor,
            student=self.user_student,
            language=self.language,
            term=self.term,
            start_time=time(10, 30),
            day_of_week="Monday",
            status="Accepted"
        )
        overlapping_booking = Booking(
            tutor=self.tutor,
            student=self.user_student,
            language=self.language,
            term=self.term,
            start_time=time(10, 30),
            day_of_week="Monday"
        )
        with self.assertRaises(Exception):
            overlapping_booking.clean()

    def test_recurring_dates(self):
        """
        Test that recurring dates are generated correctly.
        """
        booking = Booking.objects.create(
            tutor=self.tutor,
            student=self.user_student,
            language=self.language,
            term=self.term,
            start_time=time(10, 0),
            day_of_week="Monday",
            duration=timedelta(hours=1),
            frequency="Weekly"
        )
        recurring_dates = booking.get_recurring_dates()
        self.assertEqual(len(recurring_dates), 13)  
