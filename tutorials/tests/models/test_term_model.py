from django.test import TestCase
from datetime import date
from tutorials.models import Term
from django.core.exceptions import ValidationError

class TermModelTests(TestCase):
    def test_valid_term_september_christmas(self):
        """
        Test that a valid September-Christmas term can be created.
        """
        term = Term.objects.create(
            name="September-Christmas",
            start_date=date(2024, 9, 1),
            end_date=date(2024, 12, 20)
        )
        term.clean()  # Explicitly trigger validation
        self.assertEqual(term.name, "September-Christmas")
        self.assertEqual(str(term), "September-Christmas (2024-09-01 - 2024-12-20)")

    def test_invalid_term_september_christmas_dates(self):
        """
        Test that invalid start_date for September-Christmas raises ValidationError.
        """
        term = Term(
            name="September-Christmas",
            start_date=date(2024, 8, 31),  # Invalid start date
            end_date=date(2024, 12, 20)
        )
        with self.assertRaises(ValidationError):
            term.clean()

    def test_valid_term_january_easter(self):
        """
        Test that a valid January-Easter term can be created.
        """
        term = Term.objects.create(
            name="January-Easter",
            start_date=date(2025, 1, 10),
            end_date=date(2025, 4, 5)
        )
        term.clean()
        self.assertEqual(term.name, "January-Easter")

    def test_invalid_term_start_after_end(self):
        """
        Test that a term with start_date after end_date raises ValidationError.
        """
        term = Term(
            name="May-July",
            start_date=date(2024, 7, 1),
            end_date=date(2024, 6, 30)  # End date is earlier than start date
        )
        with self.assertRaises(ValidationError):
            term.clean()

    def test_invalid_term_may_july_dates(self):
        """
        Test that invalid start_date for May-July raises ValidationError.
        """
        term = Term(
            name="May-July",
            start_date=date(2024, 4, 30),  # Invalid start date
            end_date=date(2024, 7, 31)
        )
        with self.assertRaises(ValidationError):
            term.clean()

    def test_term_str_method(self):
        """
        Test the __str__() method for the Term model.
        """
        term = Term.objects.create(
            name="May-July",
            start_date=date(2024, 5, 1),
            end_date=date(2024, 7, 31)
        )
        self.assertEqual(str(term), "May-July (2024-05-01 - 2024-07-31)")
