from datetime import datetime, timezone

import pytest

from src.backend.models.bot import Bot


@pytest.fixture(autouse=True)
def cleanup_database(test_db_session):
    """Clean up the database after each test"""
    yield
    test_db_session.query(Bot).delete()
    test_db_session.commit()


def test_root_endpoint(client):
    """Test the root endpoint"""
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"status": "online"}


def test_list_bots_empty(client, test_db_session):
    """Test listing bots when there are none"""
    response = client.get("/bots/")
    assert response.status_code == 200
    assert response.json() == []


def test_list_bots_with_data(client, test_db_session):
    """Test listing bots with data"""
    bot = Bot(
        grid_id="list_test_grid",  # Unique grid_id
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

    response = client.get("/bots/")
    assert response.status_code == 200
    bots = response.json()
    assert len(bots) == 1
    assert bots[0]["grid_id"] == "list_test_grid"


def test_get_single_bot(client, test_db_session):
    """Test getting a single bot by ID"""
    bot = Bot(
        grid_id="single_test_grid",  # Unique grid_id
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

    response = client.get(f"/bots/{bot.id}")
    assert response.status_code == 200
    data = response.json()
    assert data["grid_id"] == "single_test_grid"


def test_create_bot(client):
    """Test creating a new bot"""
    bot_data = {
        "grid_id": "create_test_grid",  # Unique grid_id
        "bot_type": "futures",
        "symbol": "BTC/USDT",
        "status": "running",
        "grid_mode": "neutral",
        "price_token": "USDT",
        "grid_type": "arithmetic",
        "mark_price": 50000.0,
        "total_investment": 10000.0,
        "pnl": 100.0,
        "pnl_percentage": 1.0,
        "leverage": 5,
        "min_price": 45000.0,
        "max_price": 55000.0,
        "cell_num": 100,
        "liq_price": 40000.0,
        "arbitrage_num": 10,
        "total_apr": 15.5,
        "entry_price": 49000.0,
        "current_price": 50000.0,
        "running_duration": 3600,
        "raw_data": {"test": "data"}
    }

    response = client.post("/bots/", json=bot_data)
    assert response.status_code == 201
    data = response.json()
    assert data["grid_id"] == "create_test_grid"
