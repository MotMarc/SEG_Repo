from django.contrib import admin
from .models import User
from .models import Booking, Tutor, Language

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff')
    search_fields = ('username', 'email')
    list_filter = ('is_staff', 'is_active')

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('student', 'tutor', 'language', 'booking_time', 'status')  # Add more fields if necessary
    search_fields = ('student__username', 'tutor__user__username', 'language__name')

admin.site.register(Tutor)
admin.site.register(Language)
  