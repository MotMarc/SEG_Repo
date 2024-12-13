from django.test import TestCase
from tutorials.forms import TutorProfileForm
from tutorials.models import Language, Specialization, Tutor, User

class TutorProfileFormTests(TestCase):
    def setUp(self):
        """Set up initial data for testing."""
        self.language1 = Language.objects.create(name="Python")
        self.language2 = Language.objects.create(name="Java")
        self.specialization1 = Specialization.objects.create(name="Web Development")
        self.specialization2 = Specialization.objects.create(name="Data Science")
        self.user = User.objects.create_user(
            username='@tutoruser', password='Password123', email='tutor@example.com', account_type='tutor'
        )
        self.tutor = Tutor.objects.create(user=self.user)

    def test_valid_data(self):
        """Test valid data for TutorProfileForm."""
        form = TutorProfileForm(data={
            'languages': [self.language1.id, self.language2.id],
            'specializations': [self.specialization1.id],
        }, instance=self.tutor)
        self.assertTrue(form.is_valid())  
        tutor = form.save()
        self.assertIn(self.language1, tutor.languages.all())  
        self.assertIn(self.specialization1, tutor.specializations.all())  

    def test_missing_required_languages(self):
        """Test that missing required languages raises validation error."""
        form = TutorProfileForm(data={
            'languages': [],
            'specializations': [self.specialization1.id],
        }, instance=self.tutor)
        self.assertFalse(form.is_valid())  
        self.assertIn('languages', form.errors)  

    def test_invalid_specializations(self):
        """Test invalid specialization data."""
        form = TutorProfileForm(data={
            'languages': [self.language1.id],
            'specializations': [999],  
        }, instance=self.tutor)
        self.assertFalse(form.is_valid())  
        self.assertIn('specializations', form.errors)  
