from django.test import TestCase
from django.urls import reverse
from tutorials.models import User, Booking, Language, Term
from tutorials.forms import BookingForm

class CreateBookingViewTests(TestCase):
    def setUp(self):
        self.language = Language.objects.create(name="Python")
        self.term = Term.objects.create(name="May-July", start_date="2024-05-01", end_date="2024-07-31")
        self.user = User.objects.create_user(username="@student", password="Password123", account_type="student")

    def test_access_create_booking(self):
        """Test that authenticated users can access the create booking page."""
        self.client.login(username="@student", password="Password123")
        response = self.client.get(reverse('create_booking'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'create_booking.html')

    def test_create_booking_valid_data(self):
        """Test that a valid booking is created successfully."""
        self.client.login(username="@student", password="Password123")
        response = self.client.post(reverse('create_booking'), data={
            'language': self.language.id,
            'term': self.term.id,
            'day_of_week': 'Monday',
            'start_time': '10:00',
            'duration': '01:00:00',
            'frequency': 'Weekly',
            'experience_level': 'Intermediate level.',
        })
        self.assertEqual(response.status_code, 302)  # Redirect on success
        self.assertTrue(Booking.objects.exists())  # Booking created

    def test_create_booking_invalid_data(self):
        """Test that invalid data does not create a booking."""
        self.client.login(username="@student", password="Password123")
        response = self.client.post(reverse('create_booking'), data={
            'language': '',  # Missing language
            'term': self.term.id,
        })
        self.assertEqual(response.status_code, 200)  # Form re-rendered
        self.assertFalse(Booking.objects.exists())  # Booking not created
