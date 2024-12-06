from django.contrib import admin
from .models import User

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'account_type', 'is_staff')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    list_filter = ('account_type', 'is_staff', 'is_active')
