from requests import Session, Response
from urllib.parse import urlencode
from logger import setup_logger
import random
import json
import time


class SteamInfoCrawler:
    retry_attempts = 0

    def __init__(self):
        self._set_requests()
        self.logger = setup_logger(__name__)

    def _set_requests(self):
        self.requests = Session()
        self._set_header()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.requests.close()

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
        self.requests.headers.update(headers)

    def make_requests(self, request_type: str, endpoint: str, body: dict = {}) -> Response:
        sleep_time = random.uniform(
            0.1 * self.retry_attempts,
            0.2 * self.retry_attempts)
        time.sleep(sleep_time)
        self.logger.info(
            f"Making {request_type} request to {endpoint} with body {body}")
        if request_type == 'POST':
            resp = self.requests.post(
                endpoint, data=json.dumps(body),
                headers=self.requests.headers)
        elif request_type == 'PUT':
            resp = self.requests.put(
                endpoint, data=json.dumps(body),
                headers=self.requests.headers)
        elif request_type == 'GET':
            resp = self.requests.get(
                endpoint, headers=self.requests.headers, params=body)

        if resp.status_code in [429, 502, 504, 500, 244]:
            self.logger.warning("Too many requests error occured. Cooling down")
            time.sleep(random.uniform(1, 2))
            if self.retry_attempts < 30:
                self.retry_attempts += 1
                return self.make_requests(request_type, endpoint, body)

        if resp.status_code != 200:
            self.logger.error(
                f"Error making request with status_code {resp.status_code} with response content {resp.text}")
            try:
                resp_obj: dict = resp.json()
                if resp.status_code == 400 or \
                        resp_obj.get('message') == 'cookie not found':
                    self._set_requests()
                    self.logger.info(
                        f"Rerun {request_type} request to {endpoint} with body {body}")
                    return self.make_requests(request_type, endpoint, body)
            except json.JSONDecodeError:
                self.logger.error(f"Error making request with status_code")
        self.logger.info(
            f"Finished making {request_type} request to {endpoint} with body {body}, request took {resp.elapsed.total_seconds()}")
        return resp
