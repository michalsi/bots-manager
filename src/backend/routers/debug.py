from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from src.backend.deps import get_db, get_settings
from src.backend.logger import logger

router = APIRouter(
    prefix="/debug",
    tags=["debug"]
)


@router.get("/env")
async def debug_env():
    """Debug endpoint to check environment variables"""
    import os
    return {
        "env_vars": dict(os.environ),
        "cwd": os.getcwd(),
        "env_file_exists": os.path.exists('.env')
    }


@router.get("/database")
async def debug_database(db: Session = Depends(get_db)):
    """Debug endpoint for database information"""
    from ..database import _engine, _session_maker
    from sqlalchemy import text
    try:
        # Test database connection and get version
        version = db.execute(text("SELECT version()")).scalar()
        # Get connection pool statistics if available
        pool_info = {}
        if _engine is not None and hasattr(_engine, 'pool'):
            pool = _engine.pool
            pool_info = {
                "size": pool.size(),
                "checked_in": pool.checkedin(),
                "checked_out": pool.checkedout(),
                "overflow": pool.overflow()
            }
        return {
            "status": "connected",
            "database_url": get_settings().DATABASE_URL,
            "engine_initialized": _engine is not None,
            "session_maker_initialized": _session_maker is not None,
            "postgres_version": version,
            "pool_info": pool_info,
            "current_schema": db.execute(text("SELECT current_schema()")).scalar(),
            "connection_info": {
                "database": db.execute(text("SELECT current_database()")).scalar(),
                "user": db.execute(text("SELECT current_user")).scalar(),
                "pid": db.execute(text("SELECT pg_backend_pid()")).scalar()
            }
        }
    except Exception as e:
        logger.error(f"Database debug check failed: {e}")
        return {
            "status": "error",
            "error": str(e),
            "error_type": type(e).__name__,
            "database_url": get_settings().DATABASE_URL,
            "engine_initialized": _engine is not None,
            "session_maker_initialized": _session_maker is not None
        }
