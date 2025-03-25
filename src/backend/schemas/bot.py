from datetime import datetime
from typing import Optional, Dict, Any, Annotated

from pydantic import BaseModel, ConfigDict, Field


class BotBase(BaseModel):
    """Base Pydantic model for bot data validation."""
    grid_id: Annotated[str, Field(min_length=1, max_length=100)]
    bot_type: Annotated[str, Field(pattern=r"^[A-Za-z0-9_-]+$")]
    symbol: str
    status: str
    grid_mode: str
    price_token: str
    grid_type: str

    mark_price: float
    total_investment: Annotated[float, Field(gt=0)]
    pnl: float
    pnl_percentage: float
    leverage: Annotated[int, Field(gt=0, le=100)]
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