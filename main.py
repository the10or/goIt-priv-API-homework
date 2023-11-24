import sys
from datetime import date, timedelta
import platform

import aiohttp
import asyncio

MAX_PERIOD = 10
period = int(sys.argv[1])
if period > MAX_PERIOD:
    period = MAX_PERIOD
    print(f' УВАГА!\n'
          f'Період перевірки має бути не більше {MAX_PERIOD} днів.\n'
          f'Встановлено {period} днів.')

date_today = date.today()
API_URL = "https://api.privatbank.ua/p24api/exchange_rates?json&date="
DATE_FORMAT = "%d.%m.%Y"


async def main():
    async with aiohttp.ClientSession() as session:
        results = await asyncio.gather(*[get_json(i, session) for i in range(period - 1, -1, -1)])
        for result in results:
            process_results(result)


async def get_json(days, session):
    query_date = (date_today - timedelta(days=days)).strftime(DATE_FORMAT)
    url = f"{API_URL}{query_date}"

    try:
        async with session.get(url) as response:
            return await response.json()
    except aiohttp.ClientError:
        print(f'Помилка при отриманні даних за {query_date}')


def process_results(res):
    print(f'{res["date"]:-^20}\n')

    for item in res["exchangeRate"]:
        if item['currency'] in ('USD', 'EUR'):
            print(f'Валюта: {item['currency']}\n'
                  f'Купівля: {item['purchaseRate']}\n'
                  f'Продаж: {item['saleRate']}\n')


if __name__ == "__main__":
    if platform.system() == "Windows":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

    asyncio.run(main())
