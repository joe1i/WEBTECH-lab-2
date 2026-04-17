from django.contrib import admin
from .models import Announcement


@admin.register(Announcement)
class AnnouncementAdmin(admin.ModelAdmin):
    list_display = ['title', 'author', 'views_count', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at', 'author']
    search_fields = ['title', 'content']
    date_hierarchy = 'created_at'

    def save_model(self, request, obj, form, change):
        if not obj.pk:
            obj.author = request.user
        super().save_model(request, obj, form, change)