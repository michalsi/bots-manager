from unittest.mock import AsyncMock, patch

import httpx
import pytest
from fastapi.testclient import TestClient

from src.backend.main import app

client = TestClient(app)


@pytest.fixture
def mock_settings():
    return {
        "BYBIT_SECURE_TOKEN": "test_token",
        "BYBIT_DEVICE_ID": "test_device_id"
    }


def test_list_trading_bots_success(mock_settings):
    expected_response = {
        "success": True,
        "data": {
            "bots": [
                {
                    "id": "123",
                    "name": "Test Bot"
                }
            ]
        }
    }

    with patch("httpx.AsyncClient.post") as mock_post:
        mock_post.return_value = AsyncMock(
            status_code=200,
            json=lambda: expected_response
        )

        response = client.get("/trading-bots/", params={"page": 0, "limit": 10, "status": 0})

        assert response.status_code == 200
        assert response.json() == expected_response

        mock_post.assert_called_once()


def test_list_trading_bots_http_error(mock_settings):
    with patch("httpx.AsyncClient.post") as mock_post:
        mock_post.side_effect = httpx.HTTPStatusError(
            "Error",
            request=AsyncMock(),
            response=AsyncMock(status_code=401, text="Unauthorized")
        )

        response = client.get("/trading-bots/")

        assert response.status_code == 401
        assert "Failed to fetch trading bots" in response.json()["detail"]


def test_list_trading_bots_request_error(mock_settings):
    with patch("httpx.AsyncClient.post") as mock_post:
        mock_post.side_effect = httpx.RequestError("Connection error", request=AsyncMock())

        response = client.get("/trading-bots/")

        assert response.status_code == 500
        assert "Request failed" in response.json()["detail"]


def test_list_trading_bots_parameters():
    with patch("httpx.AsyncClient.post") as mock_post:
        mock_post.return_value = AsyncMock(
            status_code=200,
            json=lambda: {"success": True}
        )

        response = client.get("/trading-bots/?page=1&limit=50&status=1")

        assert response.status_code == 200
        mock_post.assert_called_once()
        # Verify the parameters were passed correctly
        call_kwargs = mock_post.call_args.kwargs
        assert "json" in call_kwargs
        assert call_kwargs["json"] == {"page": 1, "limit": 50, "status": 1}
