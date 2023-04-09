from urllib3.util.retry import Retry
import requests
from requests.adapters import HTTPAdapter
from logger import setup_logger
import random


class SteamInfoCrawler:

    def __init__(self):
        self.session = self._set_session()
        self._set_header()
        self.logger = setup_logger(__name__)

    def _set_session(self):
        session = requests.Session()
        retry_strategy = Retry(
            total=30,
            backoff_factor=0.1,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["GET", "PUT", "POST"],
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        return session

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.session.close()

    def _set_header(self):
        user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/111.0',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3',
            'Mozilla/5.0 (Windows NT 10.0; WOW64; Trident/7.0; AS; rv:11.0) like Gecko',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.97 Safari/537.36'
        ]

        random_user_agent = random.choice(user_agents)
        headers = {
            'User-Agent': random_user_agent,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
            "Cache-Control": "max-age=0",
        }
        self.session.headers.update(headers)

    def make_requests(self, request_type: str, endpoint: str, body: dict = {}) -> requests.Response:
        self.logger.info(
            f"Making {request_type} request to {endpoint} with body(params) {body}")
        response = None
        if request_type == 'POST':
            response = self.session.post(endpoint, json=body)
        elif request_type == 'PUT':
            response = self.session.put(endpoint, json=body)
        elif request_type == 'GET':
            response = self.session.get(endpoint, params=body)

        if response is None:
            self.logger.error(
                f"Error making {request_type} request to {endpoint} with body {body}")
        elif response.status_code != 200:
            self.logger.error(
                f"Error making {request_type} request to {endpoint} with body {body} and status code {response.status_code}")
            response.raise_for_status()

        self.logger.info(
            f"Finished making {request_type} request to {endpoint} with body {body}, request took {response.elapsed.total_seconds()}")
        return response
