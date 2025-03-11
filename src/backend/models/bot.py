from sqlalchemy import Column, Integer, String, JSON, DateTime
from sqlalchemy.sql import func

from ..database import Base

class Bot(Base):
    """
    SQLAlchemy model for trading bots.
    """
    __tablename__ = "bots"

    id = Column(Integer, primary_key=True, index=True)
    broker_bot_id = Column(String, unique=True, index=True)
    bot_type = Column(String)
    symbol = Column(String)
    status = Column(String)
    configuration = Column(JSON)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())