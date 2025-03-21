from datetime import datetime
from typing import Optional, Dict, Any

from pydantic import BaseModel, ConfigDict


class BotBase(BaseModel):
    """Base Pydantic model for bot data validation."""
    grid_id: str
    bot_type: str
    symbol: str
    status: str
    grid_mode: str
    price_token: str
    grid_type: str

    mark_price: float
    total_investment: float
    pnl: float
    pnl_percentage: float
    leverage: int
    min_price: float
    max_price: float
    cell_num: int
    liq_price: float
    arbitrage_num: int
    total_apr: float
    entry_price: float
    current_price: float

    running_duration: int
    close_detail: Optional[str] = None
    raw_data: Dict[str, Any]


class BotCreate(BotBase):
    """Pydantic model for creating a new bot."""
    pass


class Bot(BotBase):
    """Pydantic model for bot response."""
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    last_synced_at: datetime

    model_config = ConfigDict(from_attributes=True)
