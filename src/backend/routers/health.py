from typing import Dict

from fastapi import Depends, APIRouter
from pydantic import BaseModel
from sqlalchemy import text
from sqlalchemy.orm import Session

from src.backend.deps import get_db
from src.backend.logger import logger
from src.backend.services.bybit_service import check_bybit_api_health


class HealthCheck(BaseModel):
    status: str
    version: str
    dependencies: Dict[str, str]


router = APIRouter(
    prefix="/health",
    tags=["debug"]
)


@router.get("/", response_model=HealthCheck)
async def health_check(db: Session = Depends(get_db)):
    db_status = await check_database_health(db)
    bybit_status = await check_bybit_api_health()

    overall_status = "healthy" if db_status == "healthy" and bybit_status == "healthy" else "unhealthy"

    return HealthCheck(
        status=overall_status,
        version="1.0.0",
        dependencies={
            "database": db_status,
            "bybit_api": bybit_status
        }
    )


async def check_database_health(db: Session = Depends(get_db)) -> str:
    """Health check endpoint"""
    try:
        # Test database connection
        result = db.execute(text("SELECT 1")).scalar()
        return "healthy" if result == 1 else "unhealthy"
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return "unhealthy"
