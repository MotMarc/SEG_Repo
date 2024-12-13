from django.test import TestCase
from tutorials.models import Tutor, User, Language, Specialization

class TutorModelTests(TestCase):
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
        
        
        self.user_student = User.objects.create(
            username="@studentexample",
            first_name="Jane",
            last_name="Smith",
            email="jane.smith@example.com",
            account_type="student"
        )

        self.language_python = Language.objects.create(name="Python")
        self.language_java = Language.objects.create(name="Java")
        self.specialization_web = Specialization.objects.create(name="Web Development")
        self.specialization_data = Specialization.objects.create(name="Data Science")

    def test_create_tutor_success(self):
        """
        Test that a tutor can be successfully created for a user with account_type='tutor'.
        """
        tutor = Tutor.objects.create(user=self.user_tutor)
        tutor.languages.add(self.language_python)
        tutor.specializations.add(self.specialization_web)

        self.assertEqual(tutor.user, self.user_tutor)
        self.assertIn(self.language_python, tutor.languages.all())
        self.assertIn(self.specialization_web, tutor.specializations.all())
        self.assertEqual(str(tutor), "John Doe")  

    def test_create_tutor_invalid_user(self):
        """
        Test that creating a tutor for a user with account_type!='tutor' raises an error.
        """
        with self.assertRaises(Exception):
            Tutor.objects.create(user=self.user_student)

    def test_tutor_with_multiple_languages_and_specializations(self):
        """
        Test that a tutor can have multiple languages and specializations.
        """
        tutor = Tutor.objects.create(user=self.user_tutor)
        tutor.languages.add(self.language_python, self.language_java)
        tutor.specializations.add(self.specialization_web, self.specialization_data)

        self.assertEqual(tutor.languages.count(), 2)
        self.assertEqual(tutor.specializations.count(), 2)
        self.assertIn(self.language_java, tutor.languages.all())
        self.assertIn(self.specialization_data, tutor.specializations.all())

    def test_tutor_str_method(self):
        """
        Test the __str__() method for the Tutor model.
        """
        tutor = Tutor.objects.create(user=self.user_tutor)
        self.assertEqual(str(tutor), "John Doe")
