"""Модуль с задачами запускаемыми планировщиком."""
from datetime import date, datetime, timedelta

import requests
from celery import shared_task
from loguru import logger

from api.repository import (
    create_or_update_currency,
    create_rate,
    get_all_currencies,
    get_filter_by_code_and_date_rates,
)
from rates.settings import (
    API_REQUEST_TIMEOUT,
    CURRENCY_KEY_IN_API,
    DAYS_TO_LOAD_RATES,
    URL_ARCHIVE_RATES_BASE,
    URL_ARCHIVE_RATES_SUFFIX,
    URL_DAILY_RATES,
)


@shared_task(name="download_rates")
def download_rates() -> None:
    """Загрузить дневные котировки ЦБ РФ за последние n дней."""
    current_date = date.today()
    todays_rates = get_data_from_api(URL_DAILY_RATES, current_date)
    if CURRENCY_KEY_IN_API in todays_rates:
        save_currencies(todays_rates)
        save_rates(todays_rates)

    for num_day in range(1, DAYS_TO_LOAD_RATES):
        target_date = current_date - timedelta(days=num_day)
        day = datetime.strftime(target_date, "%Y/%m/%d")
        archive_url = (
            f"{URL_ARCHIVE_RATES_BASE}/{day}/{URL_ARCHIVE_RATES_SUFFIX}"
        )
        archive_rates = get_data_from_api(archive_url, target_date)
        if CURRENCY_KEY_IN_API in archive_rates:
            save_rates(archive_rates)


def get_data_from_api(url: str, target_date: date) -> dict:
    """Получить данные из API ЦБ РФ."""
    try:
        rates = requests.get(url, timeout=API_REQUEST_TIMEOUT).json()
    except Exception as exc:
        logger.error(
            f"failed to load rates from url {url} for date "
            f"{str(target_date)}: {exc}"
        )
        rates = {}

    return rates


def save_rates(rates: dict) -> None:
    """Сохранить котировки валют за конкретную дату."""
    for currency in rates[CURRENCY_KEY_IN_API]:
        if not get_filter_by_code_and_date_rates(currency, rates["Date"]):
            create_rate(
                rates["Date"],
                currency,
                rates[CURRENCY_KEY_IN_API][currency]["Value"],
            )


def save_currencies(rates: dict) -> None:
    """Сохранить валюты представленные в API ЦБ РФ."""
    if not get_all_currencies() and CURRENCY_KEY_IN_API in rates:
        for charcode in rates[CURRENCY_KEY_IN_API]:
            create_or_update_currency(charcode)
