from src.backend.models.bot import Bot


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
    # Create a test bot
    bot = Bot(
        broker_bot_id="test_bot_1",
        bot_type="grid",
        symbol="BTC/USDT",
        status="active",
        configuration={"grid_size": 10}
    )
    test_db_session.add(bot)
    test_db_session.commit()

    response = client.get("/bots/")
    assert response.status_code == 200
    bots = response.json()
    assert len(bots) == 1
    assert bots[0]["broker_bot_id"] == "test_bot_1"
