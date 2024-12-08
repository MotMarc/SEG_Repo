"""Forms for the tutorials app."""
from django import forms
from django.contrib.auth import authenticate
from django.core.validators import RegexValidator
from .models import User, Booking, Tutor, Language, Term, Lesson, Specialization
from datetime import datetime, timedelta
from django.core.exceptions import ValidationError


class LogInForm(forms.Form):
    """Form enabling registered users to log in."""

    username = forms.CharField(label="Username", widget=forms.TextInput(attrs={'class': 'form-control'}))
    password = forms.CharField(label="Password", widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    

    

    def get_user(self):
        """Returns authenticated user if possible."""
        user = None
        if self.is_valid():
            username = self.cleaned_data.get('username')
            password = self.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
        return user


class UserForm(forms.ModelForm):
    """Form to update user profiles."""

    class Meta:
        """Form options."""
        model = User
        fields = ['first_name', 'last_name', 'username', 'email']


class NewPasswordMixin(forms.Form):
    """Form mixin for new_password and password_confirmation fields."""

    new_password = forms.CharField(
        label='Password',
        widget=forms.PasswordInput(),
        validators=[RegexValidator(
            regex=r'^(?=.*[A-Z])(?=.*[a-z])(?=.*[0-9]).*$',
            message='Password must contain an uppercase character, a lowercase '
                    'character and a number'
        )]
    )
    password_confirmation = forms.CharField(label='Password confirmation', widget=forms.PasswordInput())

    def clean(self):
        """Clean the data and generate messages for any errors."""
        super().clean()
        new_password = self.cleaned_data.get('new_password')
        password_confirmation = self.cleaned_data.get('password_confirmation')
        if new_password != password_confirmation:
            self.add_error('password_confirmation', 'Confirmation does not match password.')


class PasswordForm(NewPasswordMixin):
    """Form enabling users to change their password."""

    password = forms.CharField(label='Current password', widget=forms.PasswordInput())

    def __init__(self, user=None, **kwargs):
        """Construct new form instance with a user instance."""
        super().__init__(**kwargs)
        self.user = user

    def clean(self):
        """Clean the data and generate messages for any errors."""
        super().clean()
        password = self.cleaned_data.get('password')
        if self.user is not None:
            user = authenticate(username=self.user.username, password=password)
        else:
            user = None
        if user is None:
            self.add_error('password', "Password is invalid")

    def save(self):
        """Save the user's new password."""
        new_password = self.cleaned_data['new_password']
        if self.user is not None:
            self.user.set_password(new_password)
            self.user.save()
        return self.user


class SignUpForm(NewPasswordMixin, forms.ModelForm):
    """Form enabling unregistered users to sign up."""

    class Meta:
        """Form options."""
        model = User
        fields = ['first_name', 'last_name', 'username', 'email', 'account_type']

    account_type = forms.ChoiceField(
        choices=User.ACCOUNT_TYPES,
        label="Account Type",
        required=True,
        widget=forms.Select()
    )

    def save(self):
        """Create a new user."""
        super().save(commit=False)
        user = User.objects.create_user(
            self.cleaned_data.get('username'),
            first_name=self.cleaned_data.get('first_name'),
            last_name=self.cleaned_data.get('last_name'),
            email=self.cleaned_data.get('email'),
            password=self.cleaned_data.get('new_password'),
            account_type=self.cleaned_data.get('account_type'),  # Save the account type
        )
        return user


class BookingForm(forms.ModelForm):
    """Form for students to create a booking without selecting a tutor."""

    specialization = forms.ModelChoiceField(
        queryset=Specialization.objects.all(),
        required=False,
        label="Specialized Session (Optional)"
    )

    class Meta:
        model = Booking
        # Exclude 'tutor' from the fields
        fields = [
            'language',
            'specialization',
            'term',
            'day_of_week',
            'start_time',
            'duration',
            'frequency',
            'experience_level'
        ]
        widgets = {
            'day_of_week': forms.Select(attrs={'class': 'form-control'}),
            'term': forms.Select(attrs={'class': 'form-control'}),
            'start_time': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
            'duration': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
            'frequency': forms.Select(attrs={'class': 'form-control'}),
            'experience_level': forms.Textarea(attrs={
                'rows': 3,
                'placeholder': 'Write about your experience level in maximum 100 words.',
                'class': 'form-control',
            }),
        }

    def __init__(self, *args, **kwargs):
        language_id = kwargs.pop('language_id', None)
        super().__init__(*args, **kwargs)
        if language_id:
            try:
                language = Language.objects.get(id=language_id)
                self.fields['specialization'].queryset = language.specializations.all()
            except Language.DoesNotExist:
                self.fields['specialization'].queryset = Specialization.objects.none()
        else:
            self.fields['specialization'].queryset = Specialization.objects.all()

    def clean(self):
        """Custom validation for specialization compatibility."""
        cleaned_data = super().clean()
        specialization = cleaned_data.get('specialization')
        language = cleaned_data.get('language')

        if specialization and language:
            if not specialization.languages.filter(id=language.id).exists():
                self.add_error(
                    'specialization',
                    f"The specialization '{specialization}' is not applicable to the language '{language}'."
                )

        return cleaned_data

class TutorProfileForm(forms.ModelForm):
    languages = forms.ModelMultipleChoiceField(
        queryset=Language.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=True,
        label="Teaching Languages"
    )
    specializations = forms.ModelMultipleChoiceField(
        queryset=Specialization.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False,
        label="Specializations"
    )

    class Meta:
        model = Tutor
        fields = ['languages', 'specializations']


class AdminBookingForm(forms.ModelForm):
    """Form for admins to create a booking."""

    tutor = forms.ModelChoiceField(
        queryset=Tutor.objects.all(),
        required=True,  # Make tutor selection mandatory
        label="Select Tutor"
    )

    class Meta:
        model = Booking
        fields = ['student', 'tutor', 'language', 'specialization', 'term', 'day_of_week', 'start_time', 'duration', 'frequency']
        widgets = {
            'day_of_week': forms.Select(attrs={'class': 'form-control'}),
            'term': forms.Select(attrs={'class': 'form-control'}),
            'start_time': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
            'duration': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
            'frequency': forms.Select(attrs={'class': 'form-control'}),
        }

    def clean_tutor(self):
        tutor = self.cleaned_data.get('tutor')
        if not tutor:
            raise forms.ValidationError("Please select a tutor for the booking.")
        return tutor

    def clean(self):
        """Custom validation to ensure no overlapping bookings."""
        cleaned_data = super().clean()
        tutor = cleaned_data.get('tutor')
        term = cleaned_data.get('term')
        day_of_week = cleaned_data.get('day_of_week')
        start_time = cleaned_data.get('start_time')
        duration = cleaned_data.get('duration')

        # Validate overlapping bookings
        if tutor and term and day_of_week and start_time and duration:
            end_time = (datetime.combine(datetime.today(), start_time) + duration).time()
            overlapping_bookings = Booking.objects.filter(
                tutor=tutor,
                term=term,
                day_of_week=day_of_week,
                start_time__lt=end_time,
                start_time__gte=start_time,
                status=Booking.ACCEPTED,
            ).exclude(pk=self.instance.pk)

            if overlapping_bookings.exists():
                self.add_error(None, "This tutor is already booked for the selected time.")

        return cleaned_data