import logging
from smtplib import SMTPException

from celery import shared_task
from django.core.mail import send_mail
from django.db import transaction
from django.utils import timezone

from .models import Task

logger = logging.getLogger(__name__)


def due_reminders():
    return (
        Task.objects.filter(
            completed=False,
            reminder_sent_at__isnull=True,
            remind_at__isnull=False,
            remind_at__lte=timezone.now(),
        )
        .exclude(owner__email="")
    )


@shared_task
def send_due_reminders():
    """Periodic (celery beat): queue one email job per due reminder."""
    task_ids = list(due_reminders().values_list("id", flat=True))
    for task_id in task_ids:
        send_task_reminder.delay(task_id)
    if task_ids:
        logger.info("Queued %d reminder(s)", len(task_ids))
    return len(task_ids)


@shared_task(autoretry_for=(SMTPException, OSError), retry_backoff=True, max_retries=5)
def send_task_reminder(task_id):
    """Send one reminder. The row lock makes duplicate jobs for the same task harmless."""
    with transaction.atomic():
        task = (
            due_reminders()
            .select_related("owner")
            .select_for_update(of=("self",))
            .filter(id=task_id)
            .first()
        )
        if task is None:
            return False

        when = timezone.localtime(task.remind_at).strftime("%d/%m/%Y %H:%M")
        body = f"Hola {task.owner.username},\n\nTe recordamos tu tarea: {task.title}\nProgramada para: {when}\n"
        if task.notes:
            body += f"\nNotas:\n{task.notes}\n"

        send_mail(f"Recordatorio: {task.title}", body, None, [task.owner.email])
        task.reminder_sent_at = timezone.now()
        task.save(update_fields=["reminder_sent_at"])

    logger.info("Sent reminder for task %s to %s", task.id, task.owner.email)
    return True
