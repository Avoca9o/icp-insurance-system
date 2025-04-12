import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime
from dateutil.relativedelta import relativedelta

from bot.handlers.approve_contract_handler import approve_contract_handler
from bot.models.user_info import UserInfo
from bot.models.insurance_company import InsuranceCompany
from bot.models.insurer_scheme import InsurerScheme

@pytest.fixture
def mock_update():
    update = MagicMock()
    update.callback_query = AsyncMock()
    update.callback_query.from_user.id = 123456789
    update.callback_query.edit_message_text = AsyncMock()
    return update

@pytest.fixture
def mock_context():
    return MagicMock()

@pytest.fixture
def mock_db_client():
    with patch('bot.handlers.approve_contract_handler.db_client') as mock:
        mock.get_user_by_telegram_id = AsyncMock()
        mock.get_insurer_scheme = MagicMock()
        mock.get_insurance_company_by_id = MagicMock()
        mock.update_user_info = MagicMock()
        yield mock

@pytest.fixture
def mock_icp_client():
    with patch('bot.handlers.approve_contract_handler.icp_client') as mock:
        mock.add_approved_client = MagicMock()
        yield mock

@pytest.mark.asyncio
async def test_approve_contract_handler_unauthorized(mock_update, mock_context, mock_db_client):
    # Setup
    mock_db_client.get_user_by_telegram_id.return_value = None

    # Execute
    await approve_contract_handler(mock_update, mock_context)

    # Verify
    mock_update.callback_query.edit_message_text.assert_called_once_with(
        'You are not authorized or your data is missing. Please authorize again using the /start command'
    )

@pytest.mark.asyncio
async def test_approve_contract_handler_already_approved(mock_update, mock_context, mock_db_client):
    # Setup
    user = UserInfo(
        id=1,
        telegram_id=123456789,
        is_approved=True
    )
    mock_db_client.get_user_by_telegram_id.return_value = user

    # Execute
    await approve_contract_handler(mock_update, mock_context)

    # Verify
    mock_update.callback_query.edit_message_text.assert_called_once()
    assert 'already approved' in mock_update.callback_query.edit_message_text.call_args[0][0]

@pytest.mark.asyncio
async def test_approve_contract_handler_successful_approval(mock_update, mock_context, mock_db_client, mock_icp_client):
    # Setup
    user = UserInfo(
        id=1,
        telegram_id=123456789,
        is_approved=False,
        schema_version=1,
        insurer_id=1,
        secondary_filters="test_filters"
    )
    insurer = InsuranceCompany(
        id=1,
        pay_address="test_address"
    )
    insurer_scheme = InsurerScheme(
        id=1,
        version=1,
        diagnoses_coefs="test_coefs"
    )
    
    mock_db_client.get_user_by_telegram_id.return_value = user
    mock_db_client.get_insurer_scheme.return_value = insurer_scheme
    mock_db_client.get_insurance_company_by_id.return_value = insurer

    # Execute
    await approve_contract_handler(mock_update, mock_context)

    # Verify
    assert user.is_approved is True
    assert isinstance(user.sign_date, datetime)
    assert isinstance(user.expiration_date, datetime)
    assert user.expiration_date == user.sign_date + relativedelta(years=2)
    
    mock_db_client.update_user_info.assert_called_once_with(user)
    mock_icp_client.add_approved_client.assert_called_once()
    mock_update.callback_query.edit_message_text.assert_called_once()
    assert 'successfully approved' in mock_update.callback_query.edit_message_text.call_args[0][0] 