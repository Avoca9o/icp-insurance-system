import pytest
from unittest.mock import AsyncMock, MagicMock

from bot.handlers.help_handler import help_handler

@pytest.fixture
def mock_update():
    update = MagicMock()
    update.message = AsyncMock()
    update.message.reply_text = AsyncMock()
    return update

@pytest.fixture
def mock_context():
    return MagicMock()

@pytest.mark.asyncio
async def test_help_handler(mock_update, mock_context):
    # Execute
    await help_handler(mock_update, mock_context)

    # Verify
    mock_update.message.reply_text.assert_called_once_with(
        'Contact your insurance company for help.'
    ) 