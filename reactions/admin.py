from django.contrib import admin
from .models import Reaction


@admin.register(Reaction)
class ReactionAdmin(admin.ModelAdmin):
    list_display = ['announcement', 'user', 'get_reaction_display', 'created_at']
    list_filter = ['reaction_type', 'created_at']
    search_fields = ['user__email', 'announcement__title']

    def get_reaction_display(self, obj):
        return obj.get_reaction_type_display()

    get_reaction_display.short_description = 'Тип реакції'