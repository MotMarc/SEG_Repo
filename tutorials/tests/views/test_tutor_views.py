from django.test import TestCase
from django.urls import reverse
from tutorials.models import User, Tutor

class TutorProfileViewTests(TestCase):
    def setUp(self):
        self.tutor_user = User.objects.create_user(username="@tutor", password="Password123", account_type="tutor")
        self.tutor = Tutor.objects.create(user=self.tutor_user)

    def test_access_tutor_profile(self):
        """Test that tutors can access their profile page."""
        self.client.login(username="@tutor", password="Password123")
        response = self.client.get(reverse('tutor_profile'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'tutor_profile.html')

    def test_non_tutor_access_tutor_profile(self):
        """Test that non-tutors are redirected."""
        student_user = User.objects.create_user(username="@student", password="Password123", account_type="student")
        self.client.login(username="@student", password="Password123")
        response = self.client.get(reverse('tutor_profile'))
        self.assertEqual(response.status_code, 302) 
