from django.test import TestCase
from datetime import time, date
from tutorials.models import Tutor, User, Term, TutorAvailibility

class TutorAvailabilityModelTests(TestCase):
    def setUp(self):
        """
        Set up initial data for the tests.
        """
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

    def test_valid_availability(self):
        """
        Test creating a valid TutorAvailability.
        """
        availability = TutorAvailibility.objects.create(
            tutor=self.tutor,
            term=self.term,
            day_of_week=['monday', 'wednesday'],
            start_time=time(10, 0),
            end_time=time(14, 0),
        )
        availability.clean()  
        self.assertEqual(str(availability), "John Doe (monday, wednesday): 10:00:00-14:00:00")

    def test_invalid_availability_outside_hours(self):
        """
        Test that availability outside 9:00-19:00 raises ValidationError.
        """
        availability = TutorAvailibility(
            tutor=self.tutor,
            term=self.term,
            day_of_week=['friday'],
            start_time=time(8, 0),  
            end_time=time(20, 0),  
        )
        with self.assertRaises(Exception):
            availability.clean()

    def test_invalid_availability_start_after_end(self):
        """
        Test that start_time >= end_time raises ValidationError.
        """
        availability = TutorAvailibility(
            tutor=self.tutor,
            term=self.term,
            day_of_week=['tuesday'],
            start_time=time(14, 0),
            end_time=time(10, 0),  
        )
        with self.assertRaises(Exception):
            availability.clean()
