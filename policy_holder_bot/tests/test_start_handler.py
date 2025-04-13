import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from telegram import Update, Message, User
from telegram.ext import ContextTypes

from bot.handlers.start_handler import start_handler

@pytest.fixture
def mock_update():
    update = MagicMock(spec=Update)
    update.effective_user = MagicMock(spec=User)
    update.effective_user.first_name = "Test User"
    return update

@pytest.fixture
def mock_context():
    context = MagicMock(spec=ContextTypes.DEFAULT_TYPE)
    context.user_data = {}
    return context

@pytest.mark.asyncio
async def test_start_handler_with_first_name(mock_update, mock_context):
    mock_update.message = AsyncMock(spec=Message)
    mock_update.message.reply_text = AsyncMock()

    await start_handler(mock_update, mock_context)

    mock_update.message.reply_text.assert_called_once()
    message_text = mock_update.message.reply_text.call_args[0][0]
    assert 'Hello, Test User! 👋' in message_text
    assert 'Welcome to our insurance assistant' in message_text
    assert 'Are you ready to start?' in message_text

@pytest.mark.asyncio
async def test_start_handler_without_first_name(mock_update, mock_context):
    mock_update.message = AsyncMock(spec=Message)
    mock_update.message.reply_text = AsyncMock()
    mock_update.effective_user.first_name = None

    await start_handler(mock_update, mock_context)

    mock_update.message.reply_text.assert_called_once()
    message_text = mock_update.message.reply_text.call_args[0][0]
    assert 'Hello, User! 👋' in message_text
    assert 'Welcome to our insurance assistant' in message_text
    assert 'Are you ready to start?' in message_text 