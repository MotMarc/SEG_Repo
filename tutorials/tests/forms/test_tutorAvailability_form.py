from django.test import TestCase
from datetime import time
from tutorials.forms import TutorAvailablityForm
from tutorials.models import Term, Tutor, TutorAvalibility, User

class TutorAvailabilityFormTests(TestCase):
    def setUp(self):
        """Set up initial data for testing."""
        self.term = Term.objects.create(name="May-July", start_date="2024-05-01", end_date="2024-07-31")
        self.user_tutor = User.objects.create_user(
            username='@tutoruser', password='Password123', email='tutor@example.com', account_type='tutor'
        )
        self.tutor = Tutor.objects.create(user=self.user_tutor)

    def test_valid_availability(self):
        """Test valid tutor availability."""
        form = TutorAvailablityForm(data={
            'term': self.term.id,
            'day_of_week': ['monday'],
            'start_time': time(9, 0),
            'end_time': time(17, 0),
        })
        self.assertTrue(form.is_valid())  
        availability = form.save(commit=False)
        self.assertEqual(availability.term, self.term)  

    def test_invalid_time_range(self):
        """Test that end_time earlier than start_time raises validation error."""
        form = TutorAvailablityForm(data={
            'term': self.term.id,
            'day_of_week': ['monday'],
            'start_time': time(17, 0),
            'end_time': time(9, 0),
        })
        self.assertFalse(form.is_valid()) 
        self.assertIn('end_time', form.errors) 

    def test_missing_required_fields(self):
        """Test missing required fields raise validation errors."""
        form = TutorAvailablityForm(data={
            'term': '',  
            'day_of_week': [],
            'start_time': '',
            'end_time': '',
        })
        self.assertFalse(form.is_valid())  
        self.assertIn('term', form.errors)  
        self.assertIn('day_of_week', form.errors)  
