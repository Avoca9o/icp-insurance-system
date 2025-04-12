import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from bot.handlers.main_menu_handler import main_menu_handler
from bot.models.user_info import UserInfo

@pytest.fixture
def mock_update():
    update = MagicMock()
    update.callback_query = AsyncMock()
    update.callback_query.from_user.id = 123456789
    update.callback_query.edit_message_text = AsyncMock()
    return update

@pytest.fixture
def mock_context():
    return MagicMock()

@pytest.fixture
def mock_db_client():
    with patch('bot.handlers.main_menu_handler.db_client') as mock:
        mock.get_user_by_telegram_id = MagicMock()
        yield mock

@pytest.mark.asyncio
async def test_main_menu_handler_authorized(mock_update, mock_context, mock_db_client):
    # Setup
    user = UserInfo(
        id=1,
        telegram_id=123456789,
        email="test@example.com"
    )
    mock_db_client.get_user_by_telegram_id.return_value = user

    # Execute
    await main_menu_handler(mock_update, mock_context)

    # Verify
    mock_update.callback_query.answer.assert_called_once()
    mock_update.callback_query.edit_message_text.assert_called_once()
    call_args = mock_update.callback_query.edit_message_text.call_args[0][0]
    assert 'Welcome to Main Menu!' in call_args
    assert 'Choose an action below:' in call_args

@pytest.mark.asyncio
async def test_main_menu_handler_unauthorized(mock_update, mock_context, mock_db_client):
    # Setup
    mock_db_client.get_user_by_telegram_id.return_value = None

    # Execute
    await main_menu_handler(mock_update, mock_context)

    # Verify
    mock_update.callback_query.answer.assert_called_once()
    mock_update.callback_query.edit_message_text.assert_called_once_with(
        'You are not authorized yet. Please go through the authorization process first by using /start command.'
    ) 