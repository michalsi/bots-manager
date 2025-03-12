from datetime import datetime
from typing import Optional

from sqlalchemy import String, JSON, DateTime
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from ..database import Base


class Bot(Base):
    """
    SQLAlchemy model for trading bots.
    """
    __tablename__ = "bots"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    broker_bot_id: Mapped[str] = mapped_column(String, unique=True, index=True)
    bot_type: Mapped[str]
    symbol: Mapped[str]
    status: Mapped[str]
    configuration: Mapped[dict] = mapped_column(JSON)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), onupdate=func.now())
