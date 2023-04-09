import time
import asyncio
from bs4 import BeautifulSoup
from crawler import SteamInfoCrawler
from logger import setup_logger
from discord_notification import send_messages
from data_handler import format_messages, parse_data


logging = setup_logger(__name__)


def fetch_data(url: str, params: dict):
    with SteamInfoCrawler() as crawler:
        response = crawler.make_requests(
            request_type='GET', endpoint=url, body=params)
        soup = BeautifulSoup(response.text, 'html.parser')
        return soup


def main():

    start = time.perf_counter()
    url = 'https://gg.deals/deals/'
    params = {
        "overwhelmed_positive": {
            'minSteamReviewsCount': '5000',
            'steamReviews': '9',
            'store': '4,57'
        },
        "very_positive": {
            'minSteamReviewsCount': '5000',
            'steamReviews': '8',
            'store': '4,57'
        },
    }
    results = {}
    for rating, param in params.items():
        soup = fetch_data(url, params=param)
        results[rating] = parse_data(soup)

    messages = format_messages(results)
    asyncio.run(send_messages(messages))
    end = time.perf_counter()
    logging.info(f"Process finished in {(end - start):.2f}s")


if __name__ == "__main__":
    main()
