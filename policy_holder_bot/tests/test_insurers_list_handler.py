import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from telegram import Update, CallbackQuery
from telegram.ext import ContextTypes

from bot.handlers.insurers_list_handler import insurers_list_handler

@pytest.fixture
def mock_update():
    update = MagicMock(spec=Update)
    return update

@pytest.fixture
def mock_context():
    context = MagicMock(spec=ContextTypes.DEFAULT_TYPE)
    context.user_data = {}
    return context

@pytest.fixture
def mock_db_client():
    with patch('bot.handlers.insurers_list_handler.db_client') as mock:
        yield mock

@pytest.mark.asyncio
async def test_insurers_list_handler(mock_update, mock_context, mock_db_client):
    mock_update.callback_query = AsyncMock(spec=CallbackQuery)
    mock_update.callback_query.answer = AsyncMock()
    mock_update.callback_query.edit_message_text = AsyncMock()
    
    mock_company1 = MagicMock()
    mock_company1.name = "Insurance Company 1"
    mock_company1.email = "company1@example.com"
    
    mock_company2 = MagicMock()
    mock_company2.name = "Insurance Company 2"
    mock_company2.email = "company2@example.com"
    
    mock_db_client.get_most_popular_insurers.return_value = [
        (mock_company1, 100),
        (mock_company2, 50)
    ]

    await insurers_list_handler(mock_update, mock_context)

    mock_update.callback_query.answer.assert_called_once()
    mock_update.callback_query.edit_message_text.assert_called_once()
    
    message_text = mock_update.callback_query.edit_message_text.call_args[0][0]
    assert 'Below are the most popular companies among users:' in message_text
    assert 'Insurance Company 1' in message_text
    assert 'company1@example.com' in message_text
    assert '100' in message_text
    assert 'Insurance Company 2' in message_text
    assert 'company2@example.com' in message_text
    assert '50' in message_text
    assert 'To log in, click on' in message_text 