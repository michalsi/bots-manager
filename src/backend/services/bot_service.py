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
        KeyError: If required fields are missing from the response
        ValueError: If data transformation fails
    """
    try:
        bots_data = raw_response["result"]["bots"]
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
    Args:
        raw_bot_data (dict): Single bot data from API response
    Returns:
        Bot: SQLAlchemy Bot model instance
    """

    # Extract grid data based on bot type
    bot_type = raw_bot_data["type"]
    grid_data = raw_bot_data["future_grid"]

    return Bot(
        grid_id=grid_data["grid_id"],
        bot_type=bot_type,
        symbol=grid_data["symbol"],
        status=grid_data["status"],
        grid_mode=grid_data["grid_mode"],
        price_token=grid_data["price_token"],
        grid_type=grid_data["grid_type"],

        mark_price=float(grid_data["mark_price"]),
        total_investment=float(grid_data["total_investment"]),
        pnl=float(grid_data["pnl"]),
        pnl_percentage=float(grid_data["pnl_per"]),  # Note: field name is "pnl_per" in API
        leverage=int(grid_data["leverage"]),
        min_price=float(grid_data["min_price"]),
        max_price=float(grid_data["max_price"]),
        cell_num=int(grid_data["cell_num"]),
        liq_price=float(grid_data["liq_price"]),
        arbitrage_num=int(grid_data["arbitrage_num"]),
        total_apr=float(grid_data["total_apr"]),
        entry_price=float(grid_data["entry_price"] or 0),  # Handle potential empty string
        current_price=float(grid_data["current_price"]),

        running_duration=int(grid_data["running_duration"]),
        last_synced_at=datetime.now(timezone.utc),  # Current time in UTC

        # Nullable fields
        close_detail=grid_data["close_detail"],  # Already None if null

        # Store complete original data
        raw_data=raw_bot_data  # Store the complete bot data, not just grid_data
    )


async def sync_bots_with_db(db: Session, api_response: dict) -> List[Bot]:
    """
    Sync bots from API response with database.
    Args:
        db: SQLAlchemy database session
        api_response: Raw API response containing bot data
    Returns:
        List[Bot]: List of updated/created bot instances
    """
    try:
        logger.info("Starting bot sync process")
        new_bots = extract_bot_data(api_response)
        logger.info(f"Transformed {len(new_bots)} bots from API response")
        if not new_bots:
            logger.warning("No bots to sync")
            return None
        new_grid_ids = [bot.grid_id for bot in new_bots]
        try:
            existing_bots = db.query(Bot).filter(Bot.grid_id.in_(new_grid_ids)).all()
        except SQLAlchemyError as e:
            logger.error(f"Database query failed: {str(e)}")
            raise

        existing_bots_dict: Dict[str, Bot] = dict()
        for bot in existing_bots:
            existing_bots_dict[str(bot.grid_id)] = bot

        updates = 0
        new_additions = 0

        for bot in new_bots:
            try:
                grid_id_str = str(bot.grid_id)
                if grid_id_str in existing_bots_dict:
                    existing_bot = existing_bots_dict[grid_id_str]
                    for key, value in bot.__dict__.items():
                        if key != 'id' and not key.startswith('_'):
                            setattr(existing_bot, key, value)
                    updates += 1
                else:
                    db.add(bot)
                    new_additions += 1
            except Exception as e:
                logger.error(f"Failed to process bot: {str(e)}",
                             extra={"bot": bot})
                continue
        try:
            db.commit()
            logger.info(f"Synced {updates} updated and {new_additions} new bots with database")
        except SQLAlchemyError as e:
            logger.error(f"Database commit failed: {str(e)}")
            db.rollback()
            raise
        return new_bots
    except Exception as e:
        logger.error(f"Bot sync process failed: {str(e)}")
        db.rollback()
        raise
