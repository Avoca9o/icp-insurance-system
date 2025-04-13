import pytest
import json
from unittest.mock import AsyncMock, MagicMock, patch, mock_open
from telegram import Update, CallbackQuery, User, Message
from telegram.ext import ContextTypes
from unittest.mock import ANY
from datetime import datetime

from bot.handlers.view_contract_handler import view_contract_handler
from bot.utils.docx_creator import create_docx

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
def mock_db_client():
    with patch('bot.handlers.view_contract_handler.db_client') as mock:
        yield mock

@pytest.mark.asyncio
async def test_view_contract_handler_not_authorized(mock_update, mock_context, mock_db_client):
    mock_update.callback_query = AsyncMock(spec=CallbackQuery)
    mock_update.callback_query.answer = AsyncMock()
    mock_update.callback_query.edit_message_text = AsyncMock()
    mock_db_client.get_user_by_telegram_id.return_value = None

    await view_contract_handler(mock_update, mock_context)

    mock_update.callback_query.answer.assert_called_once()
    mock_update.callback_query.edit_message_text.assert_called_once_with(
        'You are not authorized or your data is missing. Please authorize again using the /start command.'
    )

@pytest.mark.asyncio
async def test_view_contract_handler_no_scheme_no_conditions(mock_update, mock_context, mock_db_client):
    mock_update.callback_query = AsyncMock(spec=CallbackQuery)
    mock_update.callback_query.answer = AsyncMock()
    mock_update.callback_query.edit_message_text = AsyncMock()
    
    mock_user = MagicMock()
    mock_user.insurance_amount = 1000
    mock_user.insurer_id = 1
    mock_user.schema_version = 1
    mock_user.is_approved = True
    mock_user.secondary_filters = None
    
    mock_insurance_company = MagicMock()
    mock_insurance_company.name = "Test Insurance"
    
    mock_db_client.get_user_by_telegram_id.return_value = mock_user
    mock_db_client.get_insurance_company_by_id.return_value = mock_insurance_company
    mock_db_client.get_insurer_scheme.return_value = None

    await view_contract_handler(mock_update, mock_context)

    mock_update.callback_query.answer.assert_called_once()
    mock_update.callback_query.edit_message_text.assert_called_once()
    message_text = mock_update.callback_query.edit_message_text.call_args[0][0]
    assert 'Insurance amount: 💰 1000' in message_text
    assert 'Insurance company: 🏢 Test Insurance' in message_text
    assert 'User approval status: ✅ Confirmed' in message_text
    assert 'Payout coefficients: 📊 N/A' in message_text

@pytest.mark.asyncio
async def test_view_contract_handler_with_scheme_and_conditions(mock_update, mock_context, mock_db_client):
    mock_update.callback_query = AsyncMock(spec=CallbackQuery)
    mock_update.callback_query.answer = AsyncMock()
    mock_update.callback_query.edit_message_text = AsyncMock()
    mock_update.callback_query.message = AsyncMock(spec=Message)
    mock_update.callback_query.message.reply_document = AsyncMock()
    mock_update.callback_query.message.reply_text = AsyncMock()

    mock_user = MagicMock()
    mock_user.insurance_amount = 1000
    mock_user.insurer_id = 1
    mock_user.schema_version = 1
    mock_user.is_approved = True
    mock_user.secondary_filters = '{"A00.0": 0.5}'

    mock_insurance_company = MagicMock()
    mock_insurance_company.name = "Test Insurance"

    mock_insurer_scheme = MagicMock()
    mock_insurer_scheme.diagnoses_coefs = '{"A00.0": 0.5}'

    mock_db_client.get_user_by_telegram_id.return_value = mock_user
    mock_db_client.get_insurance_company_by_id.return_value = mock_insurance_company
    mock_db_client.get_insurer_scheme.return_value = mock_insurer_scheme

    with patch('bot.utils.docx_creator.Document') as mock_document:
        mock_doc = MagicMock()
        mock_document.return_value = mock_doc
        mock_doc.add_heading = MagicMock()
        mock_doc.add_paragraph = MagicMock()
        mock_doc.save = MagicMock()

        await view_contract_handler(mock_update, mock_context)

        mock_update.callback_query.answer.assert_called_once()
        mock_update.callback_query.edit_message_text.assert_called_once()
        mock_update.callback_query.message.reply_document.assert_called()
        mock_update.callback_query.message.reply_text.assert_called_once_with(
            'Return to main menu',
            reply_markup=ANY
        ) 