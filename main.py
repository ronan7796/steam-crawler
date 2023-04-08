import time
import pandas as pd
from typing import List
from concurrent.futures import ThreadPoolExecutor, as_completed
from bs4 import BeautifulSoup
from crawler import SteamInfoCrawler
from models import GameInfos
from logger import setup_logger


logging = setup_logger(__name__)


def fetch_data(url: str):
    with SteamInfoCrawler() as crawler:
        response = crawler.make_requests(request_type='GET', endpoint=url)
        soup = BeautifulSoup(response.text, 'html.parser')
        return soup


def parse_data(soup: BeautifulSoup):
    titles = soup.find_all('a', class_='game-info-title title')
    prices = soup.find_all('span', class_='price-inner game-price-new')
    discount_percents = soup.find_all('span', class_='discount label')
    drms = soup.find_all('img', class_='shop-image-white')
    links = soup.find_all('a', class_='shop-link')

    data = []
    for title, price, discount_percent, drm, link in zip(titles, prices, discount_percents, drms, links):
        data.append(GameInfos(title=title,
                              price=price,
                              discount_percent=discount_percent,
                              drm=drm,
                              link=link))
    logging.info("Parsed data from soup")
    return data


def models_to_dataframe(models: List[GameInfos]) -> pd.DataFrame:
    data = [m.dict() for m in models]
    logging.info("Converted models to pandas dataframe")
    return pd.DataFrame.from_records(data)


def run_crawler(url: str):
    soup = fetch_data(url)
    data = parse_data(soup)
    logging.info("Finished running crawler")
    return data


def main():
    start = time.perf_counter()
    min_reviews_count = 2000
    urls = {
        "overwhelmed_positive": f"https://gg.deals/deals/?minSteamReviewsCount={min_reviews_count}&steamReviews=9",
        "very_positive": f"https://gg.deals/deals/?minSteamReviewsCount={min_reviews_count}&steamReviews=8",
    }
    results = {}
    with ThreadPoolExecutor() as executor:
        futures = [executor.submit(run_crawler, url) for url in urls.values()]
        results = [models_to_dataframe(future.result())
                   for future in as_completed(futures)]
    end = time.perf_counter()
    logging.info(f"Finished, process took {(end - start):.2f}s")
    return results


if __name__ == "__main__":
    data = main()
