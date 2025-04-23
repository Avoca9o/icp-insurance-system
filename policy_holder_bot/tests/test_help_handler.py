import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from telegram import Update, Message
from telegram.ext import ContextTypes

from bot.handlers.help_handler import help_handler

@pytest.fixture
def mock_update():
    update = MagicMock(spec=Update)
    return update

@pytest.fixture
def mock_context():
    context = MagicMock(spec=ContextTypes.DEFAULT_TYPE)
    context.user_data = {}
    return context

@pytest.mark.asyncio
async def test_help_handler(mock_update, mock_context):
    mock_update.message = AsyncMock(spec=Message)
    mock_update.message.reply_text = AsyncMock()

    await help_handler(mock_update, mock_context)

    mock_update.message.reply_text.assert_called_once_with(
        'Contact your insurance company for help.'
    ) 