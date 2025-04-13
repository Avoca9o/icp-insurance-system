import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from telegram import Update, Message
from telegram.ext import ContextTypes, ConversationHandler

from bot.handlers.cancel_payout_handler import cancel_payout_handler

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
async def test_cancel_payout_handler(mock_update, mock_context):
    mock_update.message = AsyncMock(spec=Message)
    mock_update.message.reply_text = AsyncMock()

    result = await cancel_payout_handler(mock_update, mock_context)

    mock_update.message.reply_text.assert_called_once()
    assert 'Payout request process canceled.' in mock_update.message.reply_text.call_args[0][0]
    assert result == ConversationHandler.END 