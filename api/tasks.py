"""Модуль с задачами запускаемыми планировщиком."""
from datetime import date, datetime, timedelta
from django_celery_beat.models import CrontabSchedule, PeriodicTask
import requests
from api.models import Rates
from loguru import logger

from rates import settings


schedule, _ = CrontabSchedule.objects.get_or_create(
    minute='2',
    hour='*',
    day_of_week='*',
    day_of_month='*',
    month_of_year='*',
)

PeriodicTask.objects.create(
    crontab=schedule,
    name='download_rates',
    task='api.tasks.download_rates',
)


def download_rates():
    """Загрузить дневные котировки ЦБ РФ за последние n дней."""
    logger.info("start daily cron task")
    current_date = date.today()
    rates = requests.get(settings.URL_DAILY_RATES).json()
    Rates.objects.update_or_create(date=current_date, currencies=rates)

    for num_day in range(1, settings.DAYS_TO_DOWNLOAD_RATES):
        target_date = date.today() - timedelta(days=num_day)
        day = datetime.strftime(target_date, '%Y/%m/%d')
        archive_url = (f"{settings.URL_ARCHIVE_RATES}/{day}/"
                       f"{settings.URL_ARCHIVE_RATES_SUFFIX}")
        try:
            rates = requests.get(archive_url).json()
        except Exception as exc:
            logger.error(exc)
            continue
        Rates.objects.create(date=target_date, currencies=rates)



