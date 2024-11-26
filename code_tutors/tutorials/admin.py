from django.contrib import admin
from .models import User, UserProfile, LessonRequest, Lesson, Invoice

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff')
    search_fields = ('username', 'email')
    list_filter = ('is_staff', 'is_active')

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'role')
    search_fields = ('user__username', 'role')
    list_filter = ('role',)

@admin.register(LessonRequest)
class LessonRequestAdmin(admin.ModelAdmin):
    list_display = ('student', 'subject', 'status', 'created_at')
    search_fields = ('student__username', 'subject', 'description')
    list_filter = ('status',)
    ordering = ('-created_at',)

@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ('request', 'tutor', 'start_time', 'end_time')
    search_fields = ('request__subject', 'tutor__username')
    list_filter = ('start_time', 'end_time')

@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ('lesson', 'amount', 'is_paid', 'created_at')
    search_fields = ('lesson__request__subject', 'lesson__tutor__username')
    list_filter = ('is_paid', 'created_at')
    ordering = ('-created_at',)
