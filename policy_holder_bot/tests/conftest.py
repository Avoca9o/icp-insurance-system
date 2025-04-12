import pytest
from unittest.mock import MagicMock
from telegram import Update, User, Chat
from telegram.ext import ContextTypes

@pytest.fixture
def mock_update():
    update = MagicMock(spec=Update)
    update.effective_user = MagicMock(spec=User)
    update.effective_user.id = 123456789
    update.effective_user.username = "test_user"
    update.effective_chat = MagicMock(spec=Chat)
    update.effective_chat.id = 123456789
    return update

@pytest.fixture
def mock_context():
    context = MagicMock(spec=ContextTypes.DEFAULT_TYPE)
    return context

@pytest.fixture
def mock_db_client():
    return MagicMock()

@pytest.fixture
def mock_icp_client():
    return MagicMock()

@pytest.fixture
def mock_open_banking_client():
    return MagicMock()

@pytest.fixture
def mock_mailgun_client():
    return MagicMock() 