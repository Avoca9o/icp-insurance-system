import pytest
from unittest.mock import AsyncMock, MagicMock
from telegram import Update, Message
from telegram.ext import ConversationHandler

from bot.handlers.cancel_authorization_handler import cancel_authorization_handler

@pytest.mark.asyncio
async def test_cancel_authorization_handler():
    # Create mock update
    update = MagicMock(spec=Update)
    update.message = AsyncMock(spec=Message)
    update.message.reply_text = AsyncMock()

    # Create mock context
    context = MagicMock()

    # Call the handler
    result = await cancel_authorization_handler(update, context)

    # Verify the message was sent
    update.message.reply_text.assert_called_once_with(
        'Authorization process canceled. If you need help, use /start.'
    )

    # Verify the handler returned the correct state
    assert result == ConversationHandler.END 