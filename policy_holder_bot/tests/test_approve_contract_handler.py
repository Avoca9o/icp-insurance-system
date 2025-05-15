import pytest
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch
from telegram import Update, CallbackQuery, User
from telegram.ext import ContextTypes

from bot.handlers.approve_contract_handler import approve_contract_handler
from bot.models.user_info import UserInfo
from bot.models.insurer_scheme import InsurerScheme
from bot.models.company_info import CompanyInfo

@pytest.fixture
def mock_update():
    update = MagicMock(spec=Update)
    update.callback_query = AsyncMock(spec=CallbackQuery)
    update.callback_query.from_user = MagicMock(spec=User)
    update.callback_query.from_user.id = 123456789
    update.callback_query.answer = AsyncMock()
    update.callback_query.edit_message_text = AsyncMock()
    return update

@pytest.fixture
def mock_context():
    return MagicMock(spec=ContextTypes.DEFAULT_TYPE)

@pytest.fixture
def mock_db_client():
    with patch('bot.handlers.approve_contract_handler.db_client') as mock:
        yield mock

@pytest.fixture
def mock_icp_client():
    with patch('bot.handlers.approve_contract_handler.icp_client') as mock:
        yield mock

@pytest.mark.asyncio
async def test_approve_contract_handler_not_authorized(mock_update, mock_context, mock_db_client):
    mock_db_client.get_user_by_telegram_id.return_value = None

    await approve_contract_handler(mock_update, mock_context)

    mock_update.callback_query.answer.assert_called_once()
    mock_update.callback_query.edit_message_text.assert_called_once_with(
        'You are not authorized or your data is missing. Please authorize again using the /start command'
    )

@pytest.mark.asyncio
async def test_approve_contract_handler_already_approved(mock_update, mock_context, mock_db_client):
    mock_user = MagicMock(spec=UserInfo)
    mock_user.is_approved = True
    mock_db_client.get_user_by_telegram_id.return_value = mock_user

    await approve_contract_handler(mock_update, mock_context)

    mock_update.callback_query.answer.assert_called_once()
    mock_update.callback_query.edit_message_text.assert_called_once()
    assert 'Your information is already approved!' in mock_update.callback_query.edit_message_text.call_args[0][0]

@pytest.mark.asyncio
async def test_approve_contract_handler_success(mock_update, mock_context, mock_db_client, mock_icp_client):
    mock_user = MagicMock(spec=UserInfo)
    mock_user.is_approved = False
    mock_user.insurer_id = 1
    mock_user.schema_version = 1
    mock_user.secondary_filters = None

    mock_scheme = MagicMock(spec=InsurerScheme)
    mock_scheme.diagnoses_coefs = '{"A00": 0.5}'

    mock_insurer = MagicMock(spec=CompanyInfo)
    mock_insurer.pay_address = 'test_address'

    mock_db_client.get_user_by_telegram_id.return_value = mock_user
    mock_db_client.get_insurer_scheme.return_value = mock_scheme
    mock_db_client.get_insurance_company_by_id.return_value = mock_insurer
    mock_db_client.update_user_info.return_value = True

    await approve_contract_handler(mock_update, mock_context)

    mock_update.callback_query.answer.assert_called_once()
    mock_update.callback_query.edit_message_text.assert_called_once()
    assert 'Your information has been successfully approved!' in mock_update.callback_query.edit_message_text.call_args[0][0]
    
    assert mock_user.is_approved is True
    assert isinstance(mock_user.sign_date, datetime)
    assert isinstance(mock_user.expiration_date, datetime)
    mock_db_client.update_user_info.assert_called_once_with(mock_user)

@pytest.mark.asyncio
async def test_approve_contract_handler_with_special_conditions(mock_update, mock_context, mock_db_client, mock_icp_client):
    mock_user = MagicMock(spec=UserInfo)
    mock_user.is_approved = False
    mock_user.insurer_id = 1
    mock_user.schema_version = 1
    mock_user.secondary_filters = '{"A00": 0.7}'

    mock_scheme = MagicMock(spec=InsurerScheme)
    mock_scheme.diagnoses_coefs = '{"A00": 0.5}'

    mock_insurer = MagicMock(spec=CompanyInfo)
    mock_insurer.pay_address = 'test_address'

    mock_db_client.get_user_by_telegram_id.return_value = mock_user
    mock_db_client.get_insurer_scheme.return_value = mock_scheme
    mock_db_client.get_insurance_company_by_id.return_value = mock_insurer
    mock_db_client.update_user_info.return_value = True

    await approve_contract_handler(mock_update, mock_context)

    mock_update.callback_query.answer.assert_called_once()
    mock_update.callback_query.edit_message_text.assert_called_once()
    assert 'Your information has been successfully approved!' in mock_update.callback_query.edit_message_text.call_args[0][0]
    
    assert mock_user.is_approved is True
    assert isinstance(mock_user.sign_date, datetime)
    assert isinstance(mock_user.expiration_date, datetime)
    mock_db_client.update_user_info.assert_called_once_with(mock_user) 