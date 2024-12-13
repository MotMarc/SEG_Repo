from django.test import TestCase
from tutorials.models import Specialization, Language

class SpecializationModelTests(TestCase):
    def setUp(self):
        """
        Set up initial data for the tests.
        """
        self.language_python = Language.objects.create(name="Python")
        self.language_java = Language.objects.create(name="Java")

    def test_create_specialization_success(self):
        """
        Test if a specialization can be successfully created with valid data.
        """
        specialization = Specialization.objects.create(name="Web Development")
        specialization.languages.add(self.language_python, self.language_java)

        self.assertEqual(specialization.name, "Web Development")
        self.assertIn(self.language_python, specialization.languages.all())
        self.assertIn(self.language_java, specialization.languages.all())
        self.assertEqual(str(specialization), "Web Development")

    def test_duplicate_specialization_name(self):
        """
        Test that creating a specialization with a duplicate name raises an error.
        """
        Specialization.objects.create(name="Data Science")
        with self.assertRaises(Exception):
            Specialization.objects.create(name="Data Science")  

    def test_specialization_with_no_languages(self):
        """
        Test creating a specialization without associated languages.
        """
        specialization = Specialization.objects.create(name="AI Development")
        self.assertEqual(specialization.name, "AI Development")
        self.assertEqual(specialization.languages.count(), 0)

    def test_specialization_str_method(self):
        """
        Test the __str__() method of the Specialization model.
        """
        specialization = Specialization.objects.create(name="Mobile Development")
        self.assertEqual(str(specialization), "Mobile Development")
