from datetime import datetime
from typing import Optional, Dict, Any

from pydantic import BaseModel, ConfigDict


class BotBase(BaseModel):
    """
    Base Pydantic model for bot data validation.
    Defines the common attributes for both input and output.
    """
    broker_bot_id: str
    bot_type: str
    symbol: str
    status: str
    configuration: Dict[str, Any]

class BotCreate(BotBase):
    """
    Pydantic model for creating a new bot.
    Inherits from BotBase and can include additional validation if needed.
    """
    pass

class Bot(BotBase):
    """
    Pydantic model for bot response.
    Includes all fields that should be returned by the API.
    """
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)
