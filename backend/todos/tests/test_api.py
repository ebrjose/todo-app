from datetime import timedelta

from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework.test import APITestCase

from todos.models import Task

User = get_user_model()


class TaskApiTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user("ana", "ana@example.com", "una-clave-segura-1")
        self.other = User.objects.create_user("beto", "beto@example.com", "una-clave-segura-1")
        self.client.force_authenticate(self.user)

    def test_requires_authentication(self):
        self.client.force_authenticate(None)
        self.assertEqual(self.client.get("/api/tasks/").status_code, 401)

    def test_create_and_list_only_own_tasks(self):
        Task.objects.create(owner=self.other, title="ajena")
        response = self.client.post("/api/tasks/", {"title": "Comprar pan"})
        self.assertEqual(response.status_code, 201)

        titles = [t["title"] for t in self.client.get("/api/tasks/").data]
        self.assertEqual(titles, ["Comprar pan"])

    def test_cannot_touch_other_users_task(self):
        task = Task.objects.create(owner=self.other, title="ajena")
        self.assertEqual(self.client.patch(f"/api/tasks/{task.id}/", {"completed": True}).status_code, 404)
        self.assertEqual(self.client.delete(f"/api/tasks/{task.id}/").status_code, 404)

    def test_changing_remind_at_resets_sent_flag(self):
        task = Task.objects.create(
            owner=self.user, title="x", remind_at=timezone.now(), reminder_sent_at=timezone.now()
        )
        new_time = (timezone.now() + timedelta(hours=1)).isoformat()
        response = self.client.patch(f"/api/tasks/{task.id}/", {"remind_at": new_time})
        self.assertEqual(response.status_code, 200)
        self.assertIsNone(response.data["reminder_sent_at"])

    def test_other_edits_keep_sent_flag(self):
        sent = timezone.now()
        task = Task.objects.create(owner=self.user, title="x", remind_at=sent, reminder_sent_at=sent)
        self.client.patch(f"/api/tasks/{task.id}/", {"title": "y"})
        task.refresh_from_db()
        self.assertEqual(task.reminder_sent_at, sent)
