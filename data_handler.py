from bs4 import BeautifulSoup
from models import GameInfos
from logger import setup_logger
from more_itertools import batched
from typing import List, Dict
from datetime import datetime, timedelta

logging = setup_logger(__name__)


def parse_data(soup: BeautifulSoup):
    try:
        logging.info("Start parsing data from soup")
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
        logging.info(f"Done parsing {len(data)} record(s) from soup")
        return data
    except Exception as e:
        logging.exception("An error occurred while parsing data from soup")
        raise e


def format_messages(data: Dict[str, List[GameInfos]], chunk_size: int = 5, ) -> List[str]:
    try:
        messages = []
        today = datetime.now().strftime("%Y-%m-%d")
        header = f"**================== Deals of the day ({today}) ==================**\n"
        messages.append(header)
        deals = 0
        for rating, games in data.items():
            deals += len(games)
            game_chunks = batched(games, chunk_size)
            for chunk in game_chunks:
                message_lines = []
                for game in chunk:
                    game_line = (
                        f"**{game.title.upper()}**\n"
                        f"\t+ Price: {game.price}\n"
                        f"\t+ Discount: {game.discount_percent}\n"
                        f"\t+ Platform: {game.platform}\n"
                        f"\t+ Review: {rating.replace('_', ' ').title()}\n\n"
                    )
                    message_lines.append(game_line)
                messages.append(''.join(message_lines))
        logging.info(f"Done formating data into {len(messages)} message(s)")
        footer = f"**========= Total {deals} deals of the day ({today}) =========**\n"
        messages.append(footer)
        return messages
    except Exception as e:
        logging.exception("An error occurred while formatting messages")
        raise e
