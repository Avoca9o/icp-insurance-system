import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from telegram import Update, Message
from telegram.ext import ConversationHandler

from bot.handlers.cancel_payout_handler import cancel_payout_handler

@pytest.mark.asyncio
async def test_cancel_payout_handler():
    # Create mock update
    update = MagicMock(spec=Update)
    update.message = AsyncMock(spec=Message)
    update.message.reply_text = AsyncMock()

    # Create mock context
    context = MagicMock()

    # Mock the keyboard
    with patch('bot.handlers.cancel_payout_handler.get_main_menu_keyboard') as mock_keyboard:
        mock_keyboard.return_value = MagicMock()

        # Call the handler
        result = await cancel_payout_handler(update, context)

        # Verify the keyboard was created
        mock_keyboard.assert_called_once()

        # Verify the message was sent with the keyboard
        update.message.reply_text.assert_called_once_with(
            'Payout request process canceled.',
            reply_markup=mock_keyboard.return_value
        )

        # Verify the handler returned the correct state
        assert result == ConversationHandler.END 