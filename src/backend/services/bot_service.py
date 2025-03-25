import logging
from datetime import datetime, timezone
from typing import List, Dict

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from src.backend.models import Bot

logger = logging.getLogger(__name__)


def extract_bot_data(raw_response: dict) -> list[Bot]:
    """
    Transform raw API response into list of Bot models.
    Args:
        raw_response: Raw API response containing bot data
    Returns:
        List[Bot]: List of transformed bot models
    Raises:
        ValueError: If authentication failed or data transformation fails
        KeyError: If required fields are missing from the response
    """
    logger.debug(f"Raw API response: {raw_response}")

    # Check for authentication failure
    if raw_response.get("ret_code") == 10007:
        logger.error("Authentication failed with Bybit API")
        raise ValueError("Authentication failed with Bybit API")

    # Check for any other error codes
    if raw_response.get("ret_code") != 0:
        logger.error(f"API error: {raw_response.get('ret_msg')}")
        raise ValueError(f"API error: {raw_response.get('ret_msg')}")

    try:
        if "result" not in raw_response or not raw_response["result"]:
            raise ValueError("Empty or invalid result in API response")

        if "bots" in raw_response["result"]:
            bots_data = raw_response["result"]["bots"]
        else:
            bots_data = raw_response["result"]

        if not isinstance(bots_data, list):
            raise ValueError("Bot data must be a list")

        transformed_bots = []
        for bot_data in bots_data:
            try:
                transformed_bots.append(transform_bot_data(bot_data))
            except Exception as e:
                logger.error(f"Failed to transform bot data: {str(e)}",
                             extra={"bot_data": bot_data})
                continue
        return transformed_bots
    except KeyError as e:
        logger.error(f"Invalid API response structure: {str(e)}")
        raise ValueError("Invalid API response structure") from e


def transform_bot_data(raw_bot_data: dict) -> Bot:
    """
    Transform raw bot data from API response into Bot model instance.
    """
    logger.debug(f"Transforming bot data: {raw_bot_data}")  # Debug log

    # Extract grid data
    grid_data = raw_bot_data.get("grid", {})  # Check if it's under 'grid' key
    if not grid_data:
        grid_data = raw_bot_data  # Use root object if no 'grid' key

    try:
        return Bot(
            grid_id=str(grid_data.get("gridId") or grid_data.get("grid_id")),
            bot_type=raw_bot_data.get("type", "unknown"),
            symbol=grid_data.get("symbol"),
            status=grid_data.get("status"),
            grid_mode=grid_data.get("gridMode") or grid_data.get("grid_mode"),
            price_token=grid_data.get("priceToken") or grid_data.get("price_token"),
            grid_type=grid_data.get("gridType") or grid_data.get("grid_type"),

            # Convert numeric values safely
            mark_price=float(grid_data.get("markPrice", 0) or 0),
            total_investment=float(grid_data.get("totalInvestment", 0) or 0),
            pnl=float(grid_data.get("pnl", 0) or 0),
            pnl_percentage=float(grid_data.get("pnlPer", 0) or 0),
            leverage=int(grid_data.get("leverage", 1) or 1),
            min_price=float(grid_data.get("minPrice", 0) or 0),
            max_price=float(grid_data.get("maxPrice", 0) or 0),
            cell_num=int(grid_data.get("cellNum", 0) or 0),
            liq_price=float(grid_data.get("liqPrice", 0) or 0),
            arbitrage_num=int(grid_data.get("arbitrageNum", 0) or 0),
            total_apr=float(grid_data.get("totalApr", 0) or 0),
            entry_price=float(grid_data.get("entryPrice", 0) or 0),
            current_price=float(grid_data.get("currentPrice", 0) or 0),

            running_duration=int(grid_data.get("runningDuration", 0) or 0),
            last_synced_at=datetime.now(timezone.utc),
            close_detail=grid_data.get("closeDetail"),
            raw_data=raw_bot_data
        )
    except Exception as e:
        logger.error(f"Error transforming bot data: {e}", exc_info=True)
        raise ValueError(f"Failed to transform bot data: {e}")


async def sync_bots_with_db(db: Session, bots_data: Dict) -> Dict:
    """
    Sync bots data with database with improved data extraction
    """
    logger.info("Starting bot sync process")
    logger.debug(f"Received bots_data: {bots_data}")  # Debug log

    if not isinstance(bots_data, dict):
        return {
            "status": "error",
            "code": "API_ERROR",
            "message": "Invalid response structure from Bybit API"
        }

    try:
        # Check for Bybit API response structure
        ret_code = bots_data.get('retCode')
        if ret_code != 0:  # Bybit uses 0 for success
            return {
                "status": "error",
                "code": "API_ERROR",
                "message": f"Bybit API error: {bots_data.get('retMsg', 'Unknown error')}"
            }

        # Extract bots from the response
        result = bots_data.get('result', {})
        bots_list = result.get('list', [])  # Bybit usually uses 'list' for array data

        if not bots_list:
            logger.warning("No bots found in the API response")
            return {
                "status": "success",
                "message": "No bots to sync",
                "data": []
            }

        logger.debug(f"Found {len(bots_list)} bots to process")

        # Process each bot
        synced_bots = []
        for bot_data in bots_list:
            try:
                # Transform raw bot data into Bot model
                transformed_bot = extract_bot_data(bot_data)

                # Check for existing bot
                existing_bot = db.query(Bot).filter(
                    Bot.grid_id == transformed_bot.grid_id
                ).first()

                if existing_bot:
                    # Update existing bot
                    for key, value in transformed_bot.__dict__.items():
                        if key != '_sa_instance_state':
                            setattr(existing_bot, key, value)
                else:
                    # Add new bot
                    db.add(transformed_bot)

                synced_bots.append(transformed_bot)

            except Exception as e:
                logger.error(f"Error processing bot: {e}", exc_info=True)
                continue

        db.commit()

        return {
            "status": "success",
            "message": f"Successfully synced {len(synced_bots)} bots",
            "data": synced_bots
        }

    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Database error: {e}", exc_info=True)
        return {
            "status": "error",
            "code": "DB_ERROR",
            "message": str(e)
        }
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        return {
            "status": "error",
            "code": "SYNC_ERROR",
            "message": str(e)
        }
