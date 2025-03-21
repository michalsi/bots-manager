import hashlib
import hmac
import logging
import time
from contextlib import asynccontextmanager

import httpx
from fastapi import FastAPI, Depends, HTTPException
from pybit.unified_trading import HTTP
from sqlalchemy import text, engine
from sqlalchemy.orm import Session

from .config import Settings
from .database import init_db
from .deps import get_db, get_settings
from .logger import setup_basic_logging, logger
from .routers import bot


@asynccontextmanager
async def lifespan(application: FastAPI):
    """Handle startup and shutdown"""
    settings = get_settings()
    init_db(settings.DATABASE_URL)  # Ensure this line is present
    setup_basic_logging(settings.DEBUG)
    logging.info("Application starting up")
    yield
    if engine is not None:
        engine.dispose()  # Close database connections
    logging.info("Application shutting down")


app = FastAPI(
    title="Trading Bot Manager",
    description="API for managing and monitoring trading bots",
    version="0.1.0",
    lifespan=lifespan
)

app.include_router(bot.router)


@app.get("/")
async def root():
    """Root endpoint for API health check"""
    return {"status": "online"}


@app.get("/debug-env/")
async def debug_env():
    """Debug endpoint to check environment variables"""
    import os
    return {
        "env_vars": dict(os.environ),
        "cwd": os.getcwd(),
        "env_file_exists": os.path.exists('.env')
    }


@app.get("/health")
async def health_check(db: Session = Depends(get_db)):
    """Health check endpoint"""
    try:
        # Test database connection
        result = db.execute(text("SELECT 1")).scalar()
        return {
            "status": "healthy",
            "database": "connected",
            "test_query_result": result
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {
            "status": "unhealthy",
            "error": str(e)
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


@app.get("/debug/database")
async def debug_database(db: Session = Depends(get_db)):
    """Debug endpoint for database information"""
    from .database import _engine, _session_maker
    from sqlalchemy import text
    try:
        # Test database connection and get version
        version = db.execute(text("SELECT version()")).scalar()
        # Get connection pool statistics if available
        pool_info = {}
        if _engine is not None and hasattr(_engine, 'pool'):
            pool = _engine.pool
            pool_info = {
                "size": pool.size(),
                "checked_in": pool.checkedin(),
                "checked_out": pool.checkedout(),
                "overflow": pool.overflow()
            }
        return {
            "status": "connected",
            "database_url": get_settings().DATABASE_URL,
            "engine_initialized": _engine is not None,
            "session_maker_initialized": _session_maker is not None,
            "postgres_version": version,
            "pool_info": pool_info,
            "current_schema": db.execute(text("SELECT current_schema()")).scalar(),
            "connection_info": {
                "database": db.execute(text("SELECT current_database()")).scalar(),
                "user": db.execute(text("SELECT current_user")).scalar(),
                "pid": db.execute(text("SELECT pg_backend_pid()")).scalar()
            }
        }
    except Exception as e:
        logger.error(f"Database debug check failed: {e}")
        return {
            "status": "error",
            "error": str(e),
            "error_type": type(e).__name__,
            "database_url": get_settings().DATABASE_URL,
            "engine_initialized": _engine is not None,
            "session_maker_initialized": _session_maker is not None
        }
