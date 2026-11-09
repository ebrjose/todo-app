from rest_framework import serializers

from .models import Task


class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = [
            "id",
            "title",
            "notes",
            "completed",
            "remind_at",
            "reminder_sent_at",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["reminder_sent_at", "created_at", "updated_at"]

    def update(self, instance, validated_data):
        # A new reminder time means the reminder has to be sent again.
        if "remind_at" in validated_data and validated_data["remind_at"] != instance.remind_at:
            instance.reminder_sent_at = None
        return super().update(instance, validated_data)
