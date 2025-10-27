import sys
from typing import Optional, Union

import requests
from dotenv import load_dotenv
from loguru import logger

logger.remove()
logger.add(sys.stderr, level="INFO", format="<level>{level}</level> | <level>{message}</level>")
# logger.add("logs/log.log", level="DEBUG", rotation="10 MB")

if not load_dotenv():
    logger.error('Create the ".env" file using the ".env.template" example')
    exit()

class ApiClient:
    def __init__(self, base_url: str, default_headers: Optional[dict] = None):
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update(default_headers or {})

    def request(
        self,
        method: str,
        endpoint: str,
        json: Optional[Union[dict]] = None,
        params: Optional[dict] = None,
        headers: Optional[dict] = None,
        **kwargs,
    ) -> requests.Response:
        if not self.base_url:
            logger.error('Missing "BASE_URL" in .env file')
            exit()

        url = f"{self.base_url}{endpoint}"

        try:
            response = self.session.request(
                method=method,
                url=url,
                json=json,
                params=params,
                headers=headers,
                **kwargs,
            )
        except requests.exceptions.ConnectionError:
            logger.error(f'Incorrect "BASE_URL" in .env file: {self.base_url}')
            exit()

        logger.debug(
            f"{response.elapsed.total_seconds() * 1000:.0f}ms | {response.status_code} {response.reason} | {response.request.method} {response.url}"
        )

        return response

    def get(self, endpoint: str, **kwargs) -> requests.Response:
        return self.request("GET", endpoint, **kwargs)

    def post(self, endpoint: str, **kwargs) -> requests.Response:
        return self.request("POST", endpoint, **kwargs)

    def put(self, endpoint: str, **kwargs) -> requests.Response:
        return self.request("PUT", endpoint, **kwargs)

    def delete(self, endpoint: str, **kwargs) -> requests.Response:
        return self.request("DELETE", endpoint, **kwargs)
