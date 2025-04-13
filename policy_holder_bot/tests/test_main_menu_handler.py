import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from telegram import Update, CallbackQuery, User
from telegram.ext import ContextTypes

from bot.handlers.main_menu_handler import main_menu_handler

@pytest.fixture
def mock_update():
    update = MagicMock(spec=Update)
    update.effective_user = MagicMock(spec=User)
    update.effective_user.id = 123456789
    return update

@pytest.fixture
def mock_context():
    context = MagicMock(spec=ContextTypes.DEFAULT_TYPE)
    context.user_data = {}
    return context

@pytest.fixture
def mock_db_client():
    with patch('bot.handlers.main_menu_handler.db_client') as mock:
        yield mock

@pytest.mark.asyncio
async def test_main_menu_handler_authorized(mock_update, mock_context, mock_db_client):
    mock_update.callback_query = AsyncMock(spec=CallbackQuery)
    mock_update.callback_query.answer = AsyncMock()
    mock_update.callback_query.edit_message_text = AsyncMock()
    
    mock_user = MagicMock()
    mock_db_client.get_user_by_telegram_id.return_value = mock_user

    await main_menu_handler(mock_update, mock_context)

    mock_update.callback_query.answer.assert_called_once()
    mock_update.callback_query.edit_message_text.assert_called_once()
    message_text = mock_update.callback_query.edit_message_text.call_args[0][0]
    assert 'Welcome to Main Menu!' in message_text
    assert 'Choose an action below:' in message_text

@pytest.mark.asyncio
async def test_main_menu_handler_not_authorized(mock_update, mock_context, mock_db_client):
    mock_update.callback_query = AsyncMock(spec=CallbackQuery)
    mock_update.callback_query.answer = AsyncMock()
    mock_update.callback_query.edit_message_text = AsyncMock()
    
    mock_db_client.get_user_by_telegram_id.return_value = None

    await main_menu_handler(mock_update, mock_context)

    mock_update.callback_query.answer.assert_called_once()
    mock_update.callback_query.edit_message_text.assert_called_once_with(
        'You are not authorized yet. Please go through the authorization process first by using /start command.'
    ) 