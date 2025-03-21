import os
from datetime import datetime, timezone

import pytest

from src.backend.models.bot import Bot


@pytest.mark.skipif(
    not os.getenv("USE_POSTGRES_TEST_DB"),
    reason="PostgreSQL specific test"
)
def test_create_bot(test_db_session):
    """Test creating a new bot"""
    bot = Bot(
        grid_id="test_grid_1",
        bot_type="futures",
        symbol="BTC/USDT",
        status="running",
        grid_mode="neutral",
        price_token="USDT",
        grid_type="arithmetic",
        mark_price=50000.0,
        total_investment=10000.0,
        pnl=100.0,
        pnl_percentage=1.0,
        leverage=5,
        min_price=45000.0,
        max_price=55000.0,
        cell_num=100,
        liq_price=40000.0,
        arbitrage_num=10,
        total_apr=15.5,
        entry_price=49000.0,
        current_price=50000.0,
        running_duration=3600,
        last_synced_at=datetime.now(timezone.utc),
        raw_data={"test": "data"}
    )
    test_db_session.add(bot)
    test_db_session.commit()
    test_db_session.refresh(bot)

    assert bot.id is not None
    assert bot.grid_id == "test_grid_1"
    assert bot.created_at is not None


@pytest.mark.skipif(
    not os.getenv("USE_POSTGRES_TEST_DB"),
    reason="PostgreSQL specific test"
)
@pytest.mark.integration
def test_bot_unique_grid_id(test_db_session):
    """Test that grid_id must be unique"""
    bot1 = Bot(
        grid_id="test_grid_1",
        bot_type="futures",
        symbol="BTC/USDT",
        status="running",
        grid_mode="neutral",
        price_token="USDT",
        grid_type="arithmetic",
        mark_price=50000.0,
        total_investment=10000.0,
        pnl=100.0,
        pnl_percentage=1.0,
        leverage=5,
        min_price=45000.0,
        max_price=55000.0,
        cell_num=100,
        liq_price=40000.0,
        arbitrage_num=10,
        total_apr=15.5,
        entry_price=49000.0,
        current_price=50000.0,
        running_duration=3600,
        last_synced_at=datetime.now(timezone.utc),
        raw_data={"test": "data"}
    )
    test_db_session.add(bot1)
    test_db_session.commit()

    bot2 = Bot(
        grid_id="test_grid_1",  # Same grid_id
        bot_type="futures",
        symbol="ETH/USDT",
        status="running",
        grid_mode="neutral",
        price_token="USDT",
        grid_type="arithmetic",
        mark_price=50000.0,
        total_investment=10000.0,
        pnl=100.0,
        pnl_percentage=1.0,
        leverage=5,
        min_price=45000.0,
        max_price=55000.0,
        cell_num=100,
        liq_price=40000.0,
        arbitrage_num=10,
        total_apr=15.5,
        entry_price=49000.0,
        current_price=50000.0,
        running_duration=3600,
        last_synced_at=datetime.now(timezone.utc),
        raw_data={"test": "data"}
    )
    with pytest.raises(Exception):  # Should raise an integrity error
        test_db_session.add(bot2)
        test_db_session.commit()
