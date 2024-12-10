from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html

from .forms import AdminBookingForm  # Import the AdminBookingForm
from .models import (Booking, Invoice, Language, Lesson, Specialization, Term,
                     Tutor, User)


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'account_type', 'is_staff')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    list_filter = ('account_type', 'is_staff', 'is_active')


#admin booking
@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    form = AdminBookingForm  # Use the custom admin form
    list_display = ('student', 'get_tutor', 'language', 'term', 'start_time', 'frequency', 'status')
    list_filter = ('status', 'term', 'frequency', 'language')
    search_fields = ('student__username', 'tutor__user__username', 'language__name', 'term__name')
    actions = ['approve_bookings']

    def get_tutor(self, obj):
        """Return the tutor's full name for display."""
        return obj.tutor.user.full_name() if obj.tutor else "No Tutor Assigned"
    get_tutor.short_description = 'Tutor'

    def approve_bookings(self, request, queryset):
        """Custom admin action to approve selected bookings."""
        approved_count = 0
        for booking in queryset.filter(status=Booking.PENDING):
            booking.status = Booking.ACCEPTED
            booking.save()
            approved_count += 1
        self.message_user(request, f"{approved_count} booking(s) have been approved.")

    def generate_lessons(self, booking):
        """Generates lessons based on the booking's frequency and term dates."""
        from datetime import timedelta

        start_date = booking.term.start_date
        end_date = booking.term.end_date
        frequency_days = 7 if booking.frequency == 'Weekly' else 14
        current_date = start_date

        # Adjust current_date to the correct weekday based on term start_date
        while current_date.weekday() != start_date.weekday():
            current_date += timedelta(days=1)

        while current_date <= end_date:
            Lesson.objects.create(
                booking=booking,
                date=current_date,
                start_time=booking.start_time,
                duration=booking.duration
            )
            current_date += timedelta(days=frequency_days)
#...
@admin.register(Language)
class LanguageAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)


class TutorAdmin(admin.ModelAdmin):
    list_display = ('user', 'display_languages')
    search_fields = ('user__username', 'user__first_name', 'user__last_name')
    filter_horizontal = ('languages',)

    def display_languages(self, obj):
        return ", ".join([language.name for language in obj.languages.all()])
    display_languages.short_description = 'Languages'


@admin.register(Term)
class TermAdmin(admin.ModelAdmin):
    list_display = ('name', 'start_date', 'end_date')
    list_filter = ('start_date', 'end_date')
    search_fields = ('name',)


@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ('booking', 'date', 'start_time', 'duration')
    list_filter = ('date',)
    search_fields = ('booking__student__username', 'booking__tutor__user__username', 'booking__language__name')

@admin.register(Specialization)
class SpecializationAdmin(admin.ModelAdmin):  
    list_display = ('name',)
    search_fields = ('name',)
    
@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ('id', 'booking', 'tutor', 'student', 'total_hours', 'total_amount', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('booking__id', 'tutor__user__username', 'student__username')
    actions = ['mark_as_paid']

    @admin.action(description='Mark selected invoices as Paid')
    def mark_as_paid(self, request, queryset):
        """Custom action to mark selected invoices as Paid."""
        updated_count = queryset.update(status='Paid')
        self.message_user(request, f"{updated_count} invoice(s) successfully marked as Paid.")
