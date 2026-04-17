# users/admin.py
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    list_display = ['email', 'first_name', 'last_name', 'gender', 'is_active', 'created_at']
    list_filter = ['gender', 'is_active', 'created_at']
    search_fields = ['email', 'first_name', 'last_name']
    ordering = ['-created_at']

    fieldsets = UserAdmin.fieldsets + (
        ('Додаткова інформація', {
            'fields': ('gender', 'birth_date', 'avatar', 'bio')
        }),
    )