from django.test import TestCase
from django.urls import reverse
from tutorials.models import User
from tutorials.forms import LogInForm, SignUpForm
from django.contrib.auth import get_user_model


class UserModelTest(TestCase):
    def setUp(self):
        self.user_data = {
            "username": "@testuser",
            "first_name": "Test",
            "last_name": "User",
            "email": "testuser@example.com",
            "account_type": "student",
        }

    def test_create_valid_user(self):
        user = get_user_model().objects.create_user(
            username=self.user_data["username"],
            first_name=self.user_data["first_name"],
            last_name=self.user_data["last_name"],
            email=self.user_data["email"],
            account_type=self.user_data["account_type"],
            password="Password@123",  # Valid password
        )
        self.assertEqual(user.username, self.user_data["username"])
        self.assertTrue(user.check_password("Password@123"))

    def test_create_invalid_user(self):
        invalid_data = {
            "username": "invalidusername",  # Missing @
            "first_name": "Test",
            "last_name": "User",
            "email": "testuser@example.com",
            "account_type": "student",  # Dropdown value
            "password": "Password@123",  # Valid password
        }
        with self.assertRaises(ValueError):  # Validation occurs at form or model level
            User.objects.create(**invalid_data)


class SignUpFormTestCase(TestCase):
    def test_valid_sign_up_form(self):
        form_data = {
            "username": "@testuser",
            "first_name": "Test",
            "last_name": "User",
            "email": "testuser@example.com",
            "account_type": "student",
            "new_password": "Password@123",  # Correct field name
            "password_confirmation": "Password@123",  # Matching password
        }
        form = SignUpForm(data=form_data)
        if not form.is_valid():
            print("Form Errors:", form.errors)
            print("Form Data:", form.cleaned_data)
        self.assertTrue(form.is_valid())

    def test_form_must_save_correctly(self):
        form_data = {
            "username": "@testuser",
            "first_name": "Test",
            "last_name": "User",
            "email": "testuser@example.com",
            "account_type": "student",
            "new_password": "Password@123",  # Correct field name
            "password_confirmation": "Password@123",  # Matching password
        }
        form = SignUpForm(data=form_data)
        if not form.is_valid():
            print("Form Errors:", form.errors)
            print("Form Data:", form.cleaned_data)
        self.assertTrue(form.is_valid())
        user = form.save()
        self.assertIsNotNone(user.pk)

    def test_succesful_sign_up(self):
        before_count = User.objects.count()
        response = self.client.post(reverse("sign_up"), {
            "username": "@newuser",
            "first_name": "New",
            "last_name": "User",
            "email": "newuser@example.com",
            "account_type": "student",
            "new_password": "Password@123",  # Correct field name
            "password_confirmation": "Password@123",  # Matching password
        })
        after_count = User.objects.count()
        if after_count != before_count + 1:
            print("Response Context Errors:", response.context["form"].errors)
        self.assertEqual(after_count, before_count + 1)
