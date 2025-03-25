from src.backend.deps import get_settings
from src.backend.logger import logger
from src.backend.services.bybit_client import BybitClient, BybitClientConfig


def get_bybit_client() -> BybitClient:
    """Create and configure Bybit client instance"""
    settings = get_settings()
    config = BybitClientConfig(
        secure_token=settings.BYBIT_SECURE_TOKEN,
        device_id=settings.BYBIT_DEVICE_ID
    )
    return BybitClient(config)


async def check_bybit_api_health() -> str:
    """Check Bybit API health by validating API key status"""
    try:
        client = get_bybit_client()
        response = await client.check_api_status()
        return "healthy" if response.get("retCode") == 0 else "unhealthy"
    except Exception as e:
        logger.error(f"Bybit API health check failed: {e}")
        return "unhealthy"
