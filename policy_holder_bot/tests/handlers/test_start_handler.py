import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from bot.handlers.start_handler import start_handler

@pytest.fixture
def mock_update():
    update = MagicMock()
    update.effective_user = MagicMock()
    update.message = AsyncMock()
    update.message.reply_text = AsyncMock()
    return update

@pytest.fixture
def mock_context():
    return MagicMock()

@pytest.mark.asyncio
async def test_start_handler_with_first_name(mock_update, mock_context):
    # Setup
    mock_update.effective_user.first_name = "John"

    # Execute
    await start_handler(mock_update, mock_context)

    # Verify
    mock_update.message.reply_text.assert_called_once()
    call_args = mock_update.message.reply_text.call_args[0][0]
    assert 'Hello, John!' in call_args
    assert 'Welcome to our insurance assistant' in call_args
    assert 'Are you ready to start?' in call_args

@pytest.mark.asyncio
async def test_start_handler_without_first_name(mock_update, mock_context):
    # Setup
    mock_update.effective_user.first_name = None

    # Execute
    await start_handler(mock_update, mock_context)

    # Verify
    mock_update.message.reply_text.assert_called_once()
    call_args = mock_update.message.reply_text.call_args[0][0]
    assert 'Hello, User!' in call_args
    assert 'Welcome to our insurance assistant' in call_args
    assert 'Are you ready to start?' in call_args 