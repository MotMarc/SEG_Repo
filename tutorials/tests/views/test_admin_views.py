from django.test import TestCase
from django.urls import reverse
from tutorials.models import User, Booking, Term, Language

class AdminBookingViewsTests(TestCase):
    def setUp(self):
        self.language = Language.objects.create(name="Python")
        self.term = Term.objects.create(name="May-July", start_date="2024-05-01", end_date="2024-07-31")
        self.admin = User.objects.create_user(username="@admin", password="Password123", is_staff=True)
        self.booking = Booking.objects.create(
            student=None,  # Assume a student is linked
            language=self.language,
            term=self.term,
            day_of_week="Monday",
            start_time="10:00",
            duration="01:00:00",
            frequency="Weekly",
            status=Booking.PENDING
        )

    def test_access_pending_bookings(self):
        """Test that only staff can access pending bookings."""
        self.client.login(username="@admin", password="Password123")
        response = self.client.get(reverse('pending_bookings'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'admin_pending_bookings.html')

    def test_approve_booking(self):
        """Test that a staff user can approve a booking."""
        self.client.login(username="@admin", password="Password123")
        response = self.client.post(reverse('approve_booking', args=[self.booking.id]))
        self.assertEqual(response.status_code, 302)  # Redirect on success
        self.booking.refresh_from_db()
        self.assertEqual(self.booking.status, Booking.ACCEPTED)  # Booking approved

    def test_decline_booking(self):
        """Test that a staff user can decline a booking."""
        self.client.login(username="@admin", password="Password123")
        response = self.client.post(reverse('decline_booking', args=[self.booking.id]))
        self.assertEqual(response.status_code, 302)  # Redirect on success
        self.booking.refresh_from_db()
        self.assertEqual(self.booking.student_approval, Booking.STUDENT_REJECTED)  # Booking declined
