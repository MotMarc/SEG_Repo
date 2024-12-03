from django.contrib import admin
from .models import User, Booking, Tutor, Language, Term, Lesson


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff')
    search_fields = ('username', 'email')
    list_filter = ('is_staff', 'is_active')

#admin booking
@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('student', 'tutor', 'language', 'term', 'start_time', 'frequency', 'status')  
    search_fields = ('student__username', 'tutor__user__username', 'language__name')
    list_filter = ('status', 'term')
    actions = ['approve_bookings']

    def approve_bookings(self, request, queryset):
        """Custom admin action to approve selected bookings and generate lessons."""
        approved_count = 0
        for booking in queryset.filter(status=Booking.PENDING):
            booking.status = Booking.ACCEPTED
            booking.save()
            self.generate_lessons(booking)
            approved_count += 1
        self.message_user(request, f"{approved_count} booking(s) have been approved and lessons scheduled.")

    approve_bookings.short_description = "Approve selected bookings"

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
    search_fields = ('name',)
    list_filter = ('start_date', 'end_date')


@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ('booking', 'date', 'start_time', 'duration')
    list_filter = ('date',)
    search_fields = ('booking__student__username', 'booking__tutor__user__username', 'booking__language__name')