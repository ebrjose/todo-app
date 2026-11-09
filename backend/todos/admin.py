from django.contrib import admin

from .models import Task


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ["title", "owner", "completed", "remind_at", "reminder_sent_at", "created_at"]
    list_filter = ["completed"]
    search_fields = ["title", "notes", "owner__username", "owner__email"]
