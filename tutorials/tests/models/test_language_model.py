from django.test import TestCase
from tutorials.models import Language

class LanguageModelTests(TestCase):
    def test_create_language_success(self):
        """
        Test if a language can be successfully created with a valid name.
        """
        language = Language.objects.create(name="Python")
        self.assertEqual(language.name, "Python")
        self.assertEqual(str(language), "Python")

    def test_duplicate_language(self):
        """
        Test that creating a language with a duplicate name raises an error.
        """
        Language.objects.create(name="Python")
        with self.assertRaises(Exception):
            # Attempting to create a duplicate entry
            Language.objects.create(name="Python")

    def test_language_str_method(self):
        """
        Test the __str__() method for the Language model.
        """
        language = Language.objects.create(name="JavaScript")
        self.assertEqual(str(language), "JavaScript")
