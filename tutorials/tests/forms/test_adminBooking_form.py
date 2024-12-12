from django.test import TestCase
from datetime import time, timedelta
from tutorials.forms import AdminBookingForm
from tutorials.models import Tutor, User, Language, Term, TutorAvalibility, Booking

class AdminBookingFormTests(TestCase):
    def setUp(self):
        """Set up initial data for testing."""
        self.language = Language.objects.create(name="Python")
        self.user_tutor = User.objects.create_user(
            username='@tutoruser', password='Password123', email='tutor@example.com', account_type='tutor'
        )
        self.tutor = Tutor.objects.create(user=self.user_tutor)
        self.term = Term.objects.create(name="May-July", start_date="2024-05-01", end_date="2024-07-31")
        TutorAvalibility.objects.create(
            tutor=self.tutor,
            term=self.term,
            day_of_week=['monday'],
            start_time=time(9, 0),
            end_time=time(17, 0),
        )

    def test_valid_booking(self):
        """Test valid booking creation."""
        form = AdminBookingForm(data={
            'student': None,  # Assuming a student user is assigned during testing
            'tutor': self.tutor.id,
            'language': self.language.id,
            'specialization': None,
            'term': self.term.id,
            'day_of_week': 'Monday',
            'start_time': '10:00',
            'duration': timedelta(hours=1),
            'frequency': 'Weekly',
        })
        self.assertTrue(form.is_valid())  # Form should be valid
        booking = form.save(commit=False)
        self.assertEqual(booking.tutor, self.tutor)  # Tutor should match

    def test_booking_time_conflict(self):
        """Test that overlapping bookings raise validation error."""
        # Create an existing booking
        Booking.objects.create(
            tutor=self.tutor,
            term=self.term,
            day_of_week="Monday",
            start_time="10:00",
            duration=timedelta(hours=1),
            status=Booking.ACCEPTED
        )

        form = AdminBookingForm(data={
            'student': None,
            'tutor': self.tutor.id,
            'language': self.language.id,
            'specialization': None,
            'term': self.term.id,
            'day_of_week': 'Monday',
            'start_time': '10:30',  # Conflicts with existing booking
            'duration': timedelta(hours=1),
            'frequency': 'Weekly',
        })
        self.assertFalse(form.is_valid())  # Form should not be valid
        self.assertIn(None, form.errors)  # Error should be global
