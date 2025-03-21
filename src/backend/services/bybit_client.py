from dataclasses import dataclass
from typing import Dict

import httpx


@dataclass
class BybitClientConfig:
    secure_token: str
    device_id: str
    base_url: str = "https://api2.bybit.com"
    timeout: float = 30.0


class BybitClientError(Exception):
    """Base exception for Bybit client errors"""
    pass


class BybitClient:
    def __init__(self, config: BybitClientConfig):
        self.config = config
        self._headers = {
            "accept": "*/*",
            "accept-language": "en-GB,en-US;q=0.9,en;q=0.8",
            "content-type": "application/json",
            "origin": "https://www.bybit.com",
            "referer": "https://www.bybit.com/",
            "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36"
        }
        self._cookies = {
            "secure-token": config.secure_token,
            "deviceId": config.device_id,
        }

    async def get_trading_bots(
            self,
            page: int = 0,
            limit: int = 150,
            status: int = 0
    ) -> Dict:
        """
        Fetch trading bots from Bybit API.

        Args:
            page: Page number for pagination
            limit: Number of items per page
            status: Bot status filter

        Returns:
            Dict containing the API response

        Raises:
            BybitClientError: If the API request fails
        """
        endpoint = f"{self.config.base_url}/s1/bot/tradingbot/v1/list-all-bots"
        params = {"status": status, "page": page, "limit": limit}

        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    endpoint,
                    headers=self._headers,
                    cookies=self._cookies,
                    json=params,
                    timeout=self.config.timeout
                )
                response.raise_for_status()
                return response.json()

            except httpx.HTTPStatusError as e:
                raise BybitClientError(f"API request failed: {e.response.text}")
            except httpx.RequestError as e:
                raise BybitClientError(f"Request failed: {str(e)}")
