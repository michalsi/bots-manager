import logging
from typing import Dict

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from ..config import Settings
from ..deps import get_db, get_settings
from ..models.bot import Bot
from ..schemas.bot import Bot as BotSchema
from ..services.bot_service import sync_bots_with_db
from ..services.bybit_client import BybitClient, BybitClientConfig, BybitClientError

router = APIRouter(
    prefix="/bots",
    tags=["bots"]
)

logger = logging.getLogger(__name__)


def setup_basic_logging(debug_mode: bool) -> None:
    """Set up basic logging configuration"""
    logging.basicConfig(
        level=logging.DEBUG if debug_mode else logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )


@router.get("/", response_model=list[BotSchema])
async def list_bots(db: Session = Depends(get_db)):
    """
    Endpoint to list all bots.
    Uses FastAPI's dependency injection to get the database session.
    """
    try:
        stmt = select(Bot)
        result = db.execute(stmt)
        return result.scalars().all()
    except SQLAlchemyError as e:
        logger.error(f"Database error while fetching bots: {e}")
        raise HTTPException(status_code=500, detail="Database error occurred")


@router.post("/update")
async def update_trading_bots(
        db: Session = Depends(get_db),
        settings: Settings = Depends(get_settings),
        page: int = 0,
        limit: int = 150,
        status: int = 0
) -> Dict:
    """
    Update trading bots by fetching data from Bybit and syncing with database.
    """
    try:
        client = BybitClient(
            BybitClientConfig(
                secure_token=settings.BYBIT_SECURE_TOKEN,
                device_id=settings.BYBIT_DEVICE_ID
            )
        )

        try:
            bots_data = await client.get_trading_bots(page=page, limit=limit, status=status)
        except BybitClientError as e:
            logger.error(f"Bybit API error: {e.message}")
            raise HTTPException(
                status_code=e.code or 502,
                detail=e.message
            )

        logger.info("Successfully fetched data from Bybit API")
        # Continue with sync only if we have valid data
        return await sync_bots_with_db(db, bots_data)

    except HTTPException:
        raise
    except SQLAlchemyError as e:
        logger.error(f"Database error while syncing bots: {e}")
        raise HTTPException(status_code=500, detail="Database error occurred")
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")
