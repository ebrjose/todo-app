from datetime import timedelta
from unittest import mock

from django.contrib.auth import get_user_model
from django.core import mail
from django.test import TestCase
from django.utils import timezone

from todos.models import Task
from todos.tasks import send_due_reminders, send_task_reminder

User = get_user_model()


class ReminderTaskTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user("ana", "ana@example.com", "una-clave-segura-1")
        self.past = timezone.now() - timedelta(minutes=1)

    def test_sends_email_once(self):
        task = Task.objects.create(owner=self.user, title="Pagar luz", notes="Antes del 10", remind_at=self.past)

        self.assertTrue(send_task_reminder(task.id))
        self.assertFalse(send_task_reminder(task.id))

        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to, ["ana@example.com"])
        self.assertIn("Pagar luz", mail.outbox[0].subject)
        self.assertIn("Antes del 10", mail.outbox[0].body)
        task.refresh_from_db()
        self.assertIsNotNone(task.reminder_sent_at)

    def test_skips_future_completed_and_no_reminder(self):
        future = Task.objects.create(owner=self.user, title="f", remind_at=timezone.now() + timedelta(hours=1))
        done = Task.objects.create(owner=self.user, title="d", remind_at=self.past, completed=True)
        none = Task.objects.create(owner=self.user, title="n")

        for task in (future, done, none):
            self.assertFalse(send_task_reminder(task.id))
        self.assertEqual(len(mail.outbox), 0)

    def test_skips_users_without_email(self):
        user = User.objects.create_user("sinmail", "", "una-clave-segura-1")
        task = Task.objects.create(owner=user, title="x", remind_at=self.past)
        self.assertFalse(send_task_reminder(task.id))

    def test_periodic_job_queues_only_due_reminders(self):
        due = Task.objects.create(owner=self.user, title="due", remind_at=self.past)
        Task.objects.create(owner=self.user, title="later", remind_at=timezone.now() + timedelta(hours=1))

        with mock.patch.object(send_task_reminder, "delay") as delay:
            self.assertEqual(send_due_reminders(), 1)
        delay.assert_called_once_with(due.id)
