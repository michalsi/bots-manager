import os

import pytest

from src.backend.models.bot import Bot


@pytest.mark.skipif(
    not os.getenv("USE_POSTGRES_TEST_DB"),
    reason="PostgreSQL specific test"
)
def test_create_bot(test_db_session):
    """Test creating a new bot"""
    bot = Bot(
        broker_bot_id="test_bot_1",
        bot_type="grid",
        symbol="BTC/USDT",
        status="active",
        configuration={"grid_size": 10, "upper_price": 50000, "lower_price": 40000}
    )
    test_db_session.add(bot)
    test_db_session.commit()
    test_db_session.refresh(bot)

    assert bot.id is not None
    assert bot.broker_bot_id == "test_bot_1"
    assert bot.created_at is not None


@pytest.mark.skipif(
    not os.getenv("USE_POSTGRES_TEST_DB"),
    reason="PostgreSQL specific test"
)
@pytest.mark.integration
def test_bot_unique_broker_id(test_db_session):
    """Test that broker_bot_id must be unique"""
    bot1 = Bot(
        broker_bot_id="test_bot_1",
        bot_type="grid",
        symbol="BTC/USDT",
        status="active",
        configuration={}
    )
    test_db_session.add(bot1)
    test_db_session.commit()

    bot2 = Bot(
        broker_bot_id="test_bot_1",  # Same broker_bot_id
        bot_type="grid",
        symbol="ETH/USDT",
        status="active",
        configuration={}
    )
    with pytest.raises(Exception):  # Should raise an integrity error
        test_db_session.add(bot2)
        test_db_session.commit()
