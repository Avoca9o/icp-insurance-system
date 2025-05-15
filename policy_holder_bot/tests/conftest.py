import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from telegram import Update, Message, CallbackQuery, User
from telegram.ext import ContextTypes
import os
import sys

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

sys.path.insert(0, project_root)

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
def mock_message():
    message = AsyncMock(spec=Message)
    message.reply_text = AsyncMock()
    return message

@pytest.fixture
def mock_callback_query():
    callback_query = AsyncMock(spec=CallbackQuery)
    callback_query.answer = AsyncMock()
    callback_query.edit_message_text = AsyncMock()
    return callback_query

@pytest.fixture
def mock_db_client():
    with patch('bot.handlers.authorization_handler.db_client') as mock:
        yield mock

@pytest.fixture
def mock_icp_client():
    with patch('bot.handlers.request_payout_handler.icp_client') as mock:
        yield mock

@pytest.fixture
def mock_open_banking_client():
    with patch('bot.handlers.request_payout_handler.open_banking_client') as mock:
        yield mock

@pytest.fixture
def mock_mailgun_client():
    with patch('bot.handlers.authorization_handler.mailgun_client') as mock:
        yield mock 