from datetime import datetime
from typing import Optional

from sqlalchemy import String, JSON, DateTime, Float, Integer
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from ..database import Base


class Bot(Base):
    """SQLAlchemy model for trading bots."""
    __tablename__ = "bots"

    # Primary and identifying fields
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    grid_id: Mapped[str] = mapped_column(String, unique=True, index=True)

    # String fields
    bot_type: Mapped[str] = mapped_column(String)
    symbol: Mapped[str] = mapped_column(String)
    status: Mapped[str] = mapped_column(String)
    grid_mode: Mapped[str] = mapped_column(String)
    price_token: Mapped[str] = mapped_column(String)
    grid_type: Mapped[str] = mapped_column(String)

    # Numeric fields - using built-in types
    mark_price: Mapped[float] = mapped_column(Float)  # Changed from Float to float
    total_investment: Mapped[float] = mapped_column(Float)
    pnl: Mapped[float] = mapped_column(Float)
    pnl_percentage: Mapped[float] = mapped_column(Float)
    leverage: Mapped[int] = mapped_column(Integer)
    min_price: Mapped[float] = mapped_column(Float)
    max_price: Mapped[float] = mapped_column(Float)
    cell_num: Mapped[int] = mapped_column(Integer)
    liq_price: Mapped[float] = mapped_column(Float)
    arbitrage_num: Mapped[int] = mapped_column(Integer)
    total_apr: Mapped[float] = mapped_column(Float)
    entry_price: Mapped[float] = mapped_column(Float)
    current_price: Mapped[float] = mapped_column(Float)

    # Time-related fields
    running_duration: Mapped[int] = mapped_column(Integer)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), onupdate=func.now())
    last_synced_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))

    # Special fields
    close_detail: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    raw_data: Mapped[dict] = mapped_column(JSON)
