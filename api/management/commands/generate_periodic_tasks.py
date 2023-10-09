"""Модуль с командой генерации периодических задач."""
from django.core.management.base import BaseCommand
from django_celery_beat.models import CrontabSchedule, PeriodicTask


class Command(BaseCommand):
    """Команда генерации периодических задач."""

    help = 'generate periodic tasks'

    def handle(self, *args, **options):
        """Точка входа команды."""
        self.stdout.write('generate periodic tasks...')
        self.task_download_rates()

    def task_download_rates(self):
        """Создать периодическую задачу загрузки курсов валют."""
        schedule, _ = CrontabSchedule.objects.get_or_create(
            minute='*',
            hour='*',
            day_of_week='*',
            day_of_month='*',
            month_of_year='*',
        )

        PeriodicTask.objects.update_or_create(
            crontab=schedule,
            name='download_rates',
            task='download_rates',
        )

