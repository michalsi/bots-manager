import logging

logger = logging.getLogger(__name__)


def setup_basic_logging(debug_mode: bool) -> None:
    """Set up basic logging configuration"""
    logging.basicConfig(
        level=logging.DEBUG if debug_mode else logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
