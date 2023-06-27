from datetime import datetime, timedelta
import argparse

import aiohttp
import asyncio

URL = "https://api.privatbank.ua/p24api/exchange_rates"


async def exchange_rate(currencies, date):
    async with aiohttp.ClientSession() as session:
        date = date.strftime("%d.%m.%Y")
        url = f"{URL}?json&date={date}"
        headers = {"Accept": "application/json"}

        async with session.get(url, headers=headers) as response:
            try:
                data = await response.json()
                if "exchangeRate" in data:
                    rates = data["exchangeRate"]
                    w = {}
                    date_rates = {date: w}
                    for rate in rates:
                        if rate["currency"] in currencies:
                            w.update(
                                {
                                    rate["currency"]: {
                                        "sale": rate["saleRate"],
                                        "purchase": rate["purchaseRateNB"],
                                    }
                                }
                            )
                    return date_rates
            except aiohttp.ClientError as err:
                print(f"Error {err}, when occurring data")
                return None


async def fetch_exchange_rates_days(cur, days):
    tasks = []
    start_day = datetime.now()
    for i in range(days):
        date = start_day - timedelta(days=i)
        tasks.append(exchange_rate(cur, date))

    return await asyncio.gather(*tasks)


async def main(currency, num_of_days_):

    if num_of_days_ > 10:
        print("Max days 10")
        return {}

    exchange_rates = await fetch_exchange_rates_days(currency, num_of_days)
    return exchange_rates


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-c", "--currencies", nargs="*", default=["USD", "EUR"], help="Currency codes"
    )
    parser.add_argument(
        "-d", "--num_of_days", type=int, default=1, help="Number of days"
    )
    args = parser.parse_args()

    currencies = args.currencies
    num_of_days = args.num_of_days

    result = asyncio.run(main(currencies, num_of_days))
    print(result)
