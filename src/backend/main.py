import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi import Request
from fastapi.responses import JSONResponse
from sqlalchemy import engine

from .database import init_db
from .deps import get_settings
from .exceptions import AppException
from .logger import setup_basic_logging
from .routers import bot, debug, health


@asynccontextmanager
async def lifespan(application: FastAPI):
    """Handle startup and shutdown"""
    settings = get_settings()
    init_db(settings.DATABASE_URL)  # Ensure this line is present
    setup_basic_logging(settings.DEBUG)
    logging.info("Application starting up")
    yield
    if engine is not None:
        pass  # Add any cleanup code here

    logging.info("Application shutting down")


app = FastAPI(
    title="Trading Bot Manager",
    description="API for managing and monitoring trading bots",
    version="0.1.0",
    lifespan=lifespan
)

app.include_router(bot.router)
app.include_router(debug.router)
app.include_router(health.router)


@app.exception_handler(AppException)
async def app_exception_handler(request: Request, exc: AppException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"message": exc.message}
    )

@app.get("/")
async def root():
    """Root endpoint for API health check"""
    return {"status": "online"}


