from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session

from .database import engine, get_db
from .models import Base  # Updated import
from .models.bot import Bot  # Import the Bot model
from .schemas.bot import Bot as BotSchema  # Import the Bot schema

# Create database tables
Base.metadata.create_all(bind=engine)

# Initialize FastAPI application
app = FastAPI(
    title="Trading Bot Manager",
    description="API for managing and monitoring trading bots",
    version="0.1.0"
)

@app.get("/")
async def root():
    """Root endpoint for API health check"""
    return {"status": "online"}

@app.get("/bots/", response_model=list[BotSchema])
async def list_bots(db: Session = Depends(get_db)):
    """
    Endpoint to list all bots.
    Uses FastAPI's dependency injection to get the database session.
    """
    bots = db.query(Bot).all()
    return bots