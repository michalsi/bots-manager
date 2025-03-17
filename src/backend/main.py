import hashlib
import hmac
import time

import httpx
from fastapi import FastAPI, Depends, HTTPException
from pybit.unified_trading import HTTP
from sqlalchemy import select
from sqlalchemy.orm import Session

from .config import Settings
from .deps import get_db, get_settings
from .models.bot import Bot
from .schemas.bot import Bot as BotSchema

# Initialize FastAPI application
app = FastAPI(
    title="Trading Bot Manager",
    description="API for managing and monitoring trading bots",
    version="0.1.0"
)

@app.get("/")
async def root():
    """Root endpoint for API health check"""
    return {"status": "online"}

@app.get("/bots/", response_model=list[BotSchema])
async def list_bots(db: Session = Depends(get_db)):
    """
    Endpoint to list all bots.
    Uses FastAPI's dependency injection to get the database session.
    """
    stmt = select(Bot)
    result = db.execute(stmt)
    bots = result.scalars().all()
    return bots


@app.get("/debug-env/")
async def debug_env():
    """Debug endpoint to check environment variables"""
    import os
    return {
        "env_vars": dict(os.environ),
        "cwd": os.getcwd(),
        "env_file_exists": os.path.exists('.env')
    }


@app.get("/wallet_balance/")
async def get_wallet_balance(coin: str, settings: Settings = Depends(get_settings)):
    """Endpoint to get wallet balance for a specific coin."""
    session = HTTP(
        testnet=False,  # Set to False for production
        api_key=settings.API_KEY,
        api_secret=settings.API_SECRET,
    )
    try:
        response = session.get_wallet_balance(accountType="UNIFIED", coin=coin)
        print(f"Full response: {response}")
        if "result" in response:
            return response["result"]
        else:
            raise HTTPException(status_code=400, detail="Failed to fetch wallet balance")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


async def get_bybit_server_time() -> float:
    """Get Bybit server time."""
    async with httpx.AsyncClient() as client:
        response = await client.get("https://api.bybit.com/v5/market/time")
        data = response.json()
        return float(data["result"]["timeSecond"]) * 1000  # Convert to milliseconds


@app.get("/trading-bots/")
async def list_trading_bots(
        settings: Settings = Depends(get_settings),
        page: int = 0,
        limit: int = 150,
        status: int = 0
):
    """Endpoint to list all trading bots from Bybit using session authentication."""

    endpoint = "https://api2.bybit.com/s1/bot/tradingbot/v1/list-all-bots"

    params = {
        "status": status,
        "page": page,
        "limit": limit
    }

    headers = {
        "accept": "*/*",
        "accept-language": "en-GB,en-US;q=0.9,en;q=0.8",
        "content-type": "application/json",
        "origin": "https://www.bybit.com",
        "referer": "https://www.bybit.com/",
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36"
    }

    cookies = {
        "secure-token": settings.BYBIT_SECURE_TOKEN,
        "deviceId": settings.BYBIT_DEVICE_ID,
    }

    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                endpoint,
                headers=headers,
                cookies=cookies,
                json=params,
                timeout=30.0
            )

            print(f"Response Status: {response.status_code}")
            print(f"Response Body: {response.text}")

            response.raise_for_status()
            return response.json()

        except httpx.HTTPStatusError as e:
            raise HTTPException(
                status_code=e.response.status_code,
                detail=f"Failed to fetch trading bots: {e.response.text}"
            )
        except httpx.RequestError as e:
            raise HTTPException(
                status_code=500,
                detail=f"Request failed: {str(e)}"
            )


@app.get("/test-auth/")
async def test_auth(settings: Settings = Depends(get_settings)):
    """Test endpoint to verify API authentication."""
    current_time = int(time.time() * 1000)
    timestamp = str(current_time)
    # Simple GET request to check wallet balance
    endpoint = "https://api.bybit.com/v5/account/wallet-balance"
    params = {"accountType": "UNIFIED"}
    # Create query string for signature
    query_string = "&".join([f"{k}={v}" for k, v in sorted(params.items())])
    # Create signature with query parameters included
    signature_payload = f"{timestamp}{settings.API_KEY}5000{query_string}"
    print(f"Test Auth Signature Payload: {signature_payload}")  # Debug print
    signature = hmac.new(
        bytes(settings.API_SECRET, "utf-8"),
        bytes(signature_payload, "utf-8"),
        hashlib.sha256
    ).hexdigest()
    headers = {
        "X-BAPI-API-KEY": settings.API_KEY,
        "X-BAPI-TIMESTAMP": timestamp,
        "X-BAPI-SIGN": signature,
        "X-BAPI-RECV-WINDOW": "5000",
    }
    print(f"Test Auth Headers: {headers}")  # Debug print
    async with httpx.AsyncClient() as client:
        response = await client.get(endpoint, headers=headers, params=params)
        print(f"Test Auth Response: {response.text}")  # Debug print
        return response.json()
