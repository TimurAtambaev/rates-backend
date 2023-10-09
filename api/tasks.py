"""Модуль с задачами запускаемыми планировщиком."""
from datetime import date, datetime, timedelta
import requests
from celery import shared_task

from api.models import Rates
from loguru import logger

from rates import settings


@shared_task(name='download_rates')
def download_rates():
    """Загрузить дневные котировки ЦБ РФ за последние n дней."""
    current_date = date.today()
    todays_rates = get_data_from_api(settings.URL_DAILY_RATES, current_date)
    Rates.objects.update_or_create(id=1,
                                   date=current_date,
                                   currencies=todays_rates)

    for num_day in range(1, settings.DAYS_TO_LOAD_RATES):
        target_date = current_date - timedelta(days=num_day)
        day = datetime.strftime(target_date, '%Y/%m/%d')
        archive_url = (f"{settings.URL_ARCHIVE_RATES}/{day}/"
                       f"{settings.URL_ARCHIVE_RATES_SUFFIX}")
        archive_rates = get_data_from_api(archive_url, target_date)
        Rates.objects.update_or_create(id=num_day + 1,
                                       date=target_date,
                                       currencies=archive_rates)


def get_data_from_api(url: str, target_date: date) -> dict:
    """Получить данные из API ЦБ РФ за конкретную дату."""
    try:
        rates = requests.get(url).json()
    except Exception as exc:
        logger.error(f"failed to load rates from url {url} for date "
                     f"{str(target_date)}: {exc}")
        rates = None

    return rates

