import json
import pytest
from unittest.mock import AsyncMock, MagicMock, patch, mock_open

from bot.handlers.view_contract_handler import view_contract_handler
from bot.models.user_info import UserInfo
from bot.models.insurance_company import InsuranceCompany
from bot.models.insurer_scheme import InsurerScheme

@pytest.fixture
def mock_update():
    update = MagicMock()
    update.callback_query = AsyncMock()
    update.callback_query.from_user.id = 123456789
    update.callback_query.edit_message_text = AsyncMock()
    update.callback_query.message = MagicMock()
    update.callback_query.message.reply_document = AsyncMock()
    update.callback_query.message.reply_text = AsyncMock()
    return update

@pytest.fixture
def mock_context():
    return MagicMock()

@pytest.fixture
def mock_db_client():
    with patch('bot.handlers.view_contract_handler.db_client') as mock:
        mock.get_user_by_telegram_id = MagicMock()
        mock.get_insurance_company_by_id = MagicMock()
        mock.get_insurer_scheme = MagicMock()
        yield mock

@pytest.fixture
def mock_create_docx():
    with patch('bot.handlers.view_contract_handler.create_docx_file') as mock:
        yield mock

@pytest.fixture
def mock_os():
    with patch('bot.handlers.view_contract_handler.os') as mock:
        mock.remove = MagicMock()
        yield mock

@pytest.mark.asyncio
async def test_view_contract_handler_unauthorized(mock_update, mock_context, mock_db_client):
    # Setup
    mock_db_client.get_user_by_telegram_id.return_value = None

    # Execute
    await view_contract_handler(mock_update, mock_context)

    # Verify
    mock_update.callback_query.edit_message_text.assert_called_once_with(
        'You are not authorized or your data is missing. Please authorize again using the /start command.'
    )

@pytest.mark.asyncio
async def test_view_contract_handler_basic_info(mock_update, mock_context, mock_db_client):
    # Setup
    user = UserInfo(
        id=1,
        telegram_id=123456789,
        insurance_amount=1000,
        insurer_id=1,
        schema_version=1,
        is_approved=True
    )
    insurance_company = InsuranceCompany(
        id=1,
        name="Test Insurance"
    )
    
    mock_db_client.get_user_by_telegram_id.return_value = user
    mock_db_client.get_insurance_company_by_id.return_value = insurance_company
    mock_db_client.get_insurer_scheme.return_value = None

    # Execute
    await view_contract_handler(mock_update, mock_context)

    # Verify
    mock_update.callback_query.edit_message_text.assert_called_once()
    call_args = mock_update.callback_query.edit_message_text.call_args[0][0]
    assert 'Insurance amount: 💰 1000' in call_args
    assert 'Insurance company: 🏢 Test Insurance' in call_args
    assert 'User approval status: ✅ Confirmed' in call_args

@pytest.mark.asyncio
async def test_view_contract_handler_with_documents(
    mock_update, mock_context, mock_db_client, mock_create_docx, mock_os
):
    # Setup
    user = UserInfo(
        id=1,
        telegram_id=123456789,
        insurance_amount=1000,
        insurer_id=1,
        schema_version=1,
        is_approved=True,
        secondary_filters='{"condition": "test"}'
    )
    insurance_company = InsuranceCompany(
        id=1,
        name="Test Insurance"
    )
    insurer_scheme = InsurerScheme(
        id=1,
        diagnoses_coefs='{"coef": 1.5}'
    )
    
    mock_db_client.get_user_by_telegram_id.return_value = user
    mock_db_client.get_insurance_company_by_id.return_value = insurance_company
    mock_db_client.get_insurer_scheme.return_value = insurer_scheme

    # Mock file operations
    mock_file = mock_open()
    with patch('builtins.open', mock_file):
        # Execute
        await view_contract_handler(mock_update, mock_context)

    # Verify basic info
    mock_update.callback_query.edit_message_text.assert_called_once()
    call_args = mock_update.callback_query.edit_message_text.call_args[0][0]
    assert 'Insurance amount: 💰 1000' in call_args
    assert 'Insurance company: 🏢 Test Insurance' in call_args
    assert 'User approval status: ✅ Confirmed' in call_args

    # Verify document creation and sending
    assert mock_create_docx.call_count == 2
    assert mock_update.callback_query.message.reply_document.call_count == 2
    assert mock_os.remove.call_count == 2

    # Verify return to main menu
    mock_update.callback_query.message.reply_text.assert_called_once_with(
        'Return to main menu',
        reply_markup=mock_update.callback_query.message.reply_text.call_args[1]['reply_markup']
    ) 