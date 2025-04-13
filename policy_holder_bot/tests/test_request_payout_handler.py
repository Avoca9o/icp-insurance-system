import json
from datetime import datetime, date
import pytest
from unittest.mock import MagicMock, patch
from telegram import Update, CallbackQuery, User, Message
from telegram.ext import ContextTypes, ConversationHandler
from unittest.mock import AsyncMock

from bot.handlers.request_payout_handler import (
    request_payout_handler,
    approve_access,
    request_policy_number,
    request_diagnosis_code,
    request_diagnosis_date,
    request_crypto_wallet,
    process_payout,
    APPROVE_ACCESS,
    REQUEST_POLICY_NUMBER,
    REQUEST_DIAGNOSIS_CODE,
    REQUEST_DIAGNOSIS_TIME,
    REQUEST_CRYPTO_WALLET,
)
from bot.models.user_info import UserInfo as DBUser
from bot.models.company_info import CompanyInfo as InsuranceCompany
from bot.models.insurer_scheme import InsurerScheme as InsuranceScheme

@pytest.fixture
def mock_context():
    context = MagicMock()
    context.user_data = {}
    return context

@pytest.fixture
def mock_update():
    update = MagicMock(spec=Update)
    user = MagicMock(spec=User)
    user.id = 12345
    query = MagicMock(spec=CallbackQuery)
    query.from_user = user
    update.callback_query = query
    return update

@pytest.fixture
def mock_db_user():
    user = DBUser(
        phone="+1234567890",
        email="test@example.com",
        insurance_amount=100000,
        payout_address="test_wallet",
        insurer_id=1,
        schema_version=1,
        secondary_filters=None
    )
    user.telegram_id = 12345
    user.is_approved = True
    user.sign_date = datetime(2024, 1, 1)
    user.expiration_date = datetime(2025, 1, 1)
    return user

@pytest.fixture
def mock_insurance_company():
    company = InsuranceCompany(
        login="test_login",
        password="test_password",
        name="Test Insurance",
        email="company@test.com",
        pay_address="test_wallet"
    )
    return company

@pytest.fixture
def mock_insurance_scheme():
    scheme = InsuranceScheme(
        company_id=1,
        diagnoses_coefs='{"A00": 0.5}'
    )
    return scheme

@pytest.mark.asyncio
async def test_request_payout_handler_unauthorized(mock_update, mock_context):
    with patch('bot.handlers.request_payout_handler.db_client') as mock_db:
        mock_db.get_user_by_telegram_id.return_value = None
        
        result = await request_payout_handler(mock_update, mock_context)
        
        assert result == ConversationHandler.END
        mock_update.callback_query.edit_message_text.assert_called_once_with(
            'You are not authorized. Please authorize using the /start command.'
        )

@pytest.mark.asyncio
async def test_request_payout_handler_not_approved(mock_update, mock_context, mock_db_user):
    mock_db_user.is_approved = False
    with patch('bot.handlers.request_payout_handler.db_client') as mock_db:
        mock_db.get_user_by_telegram_id.return_value = mock_db_user
        
        result = await request_payout_handler(mock_update, mock_context)
        
        assert result == ConversationHandler.END
        assert mock_update.callback_query.edit_message_text.call_args[0][0].startswith(
            'Your contract information is not approved yet'
        )

@pytest.mark.asyncio
async def test_request_payout_handler_success(mock_update, mock_context, mock_db_user):
    with patch('bot.handlers.request_payout_handler.db_client') as mock_db:
        mock_db.get_user_by_telegram_id.return_value = mock_db_user
        
        result = await request_payout_handler(mock_update, mock_context)
        
        assert result == APPROVE_ACCESS
        assert mock_update.callback_query.edit_message_text.call_args[0][0].startswith(
            'To process payout request'
        )

@pytest.mark.asyncio
async def test_approve_access_confirm(mock_update, mock_context):
    mock_update.callback_query.data = 'confirm_personal_data'
    with patch('bot.handlers.request_payout_handler.open_banking_client') as mock_banking:
        mock_banking.get_oauth_token = AsyncMock(return_value='test_token')
        
        result = await approve_access(mock_update, mock_context)
        
        assert result == REQUEST_POLICY_NUMBER
        assert mock_context.user_data['oauth_token'] == 'test_token'
        mock_update.callback_query.edit_message_text.assert_called_once_with(
            'Personal data access confirmed. ✅\n\nPlease enter your policy number:'
        )

@pytest.mark.asyncio
async def test_approve_access_cancel(mock_update, mock_context):
    # Подготовка
    mock_update.callback_query = AsyncMock()
    mock_update.callback_query.data = 'cancel'
    mock_update.callback_query.message = AsyncMock()
    mock_update.callback_query.message.edit_message_text = AsyncMock()
    mock_update.callback_query.answer = AsyncMock()

    with patch('bot.handlers.request_payout_handler.open_banking_client') as mock_banking_client, \
         patch('bot.handlers.request_payout_handler.get_main_menu_keyboard') as mock_keyboard:
        mock_banking_client.get_oauth_token = AsyncMock(return_value='test_token')
        mock_keyboard.return_value = None

        # Выполнение
        result = await approve_access(mock_update, mock_context)

        # Проверка
        mock_update.callback_query.answer.assert_called_once()
        mock_update.callback_query.edit_message_text.assert_called_once_with(
            'Payout request canceled. ❌',
            reply_markup=None
        )
        assert result == ConversationHandler.END

@pytest.mark.asyncio
async def test_request_policy_number_valid(mock_update, mock_context):
    mock_message = MagicMock(spec=Message)
    mock_message.text = "123456789"
    mock_update.message = mock_message
    
    result = await request_policy_number(mock_update, mock_context)
    
    assert result == REQUEST_DIAGNOSIS_CODE
    assert mock_context.user_data['policy_number'] == "123456789"
    mock_update.message.reply_text.assert_called_once_with(
        'Please enter the diagnosis code:'
    )

@pytest.mark.asyncio
async def test_request_policy_number_invalid(mock_update, mock_context):
    mock_message = MagicMock(spec=Message)
    mock_message.text = "invalid"
    mock_update.message = mock_message
    mock_update.message.reply_text = AsyncMock()

    result = await request_policy_number(mock_update, mock_context)

    mock_update.message.reply_text.assert_called_once_with(
        'Invalid policy number. Try again'
    )
    assert result == REQUEST_POLICY_NUMBER

@pytest.mark.asyncio
async def test_request_diagnosis_code_valid(mock_update, mock_context):
    mock_message = MagicMock(spec=Message)
    mock_message.text = "A00"
    mock_update.message = mock_message
    
    result = await request_diagnosis_code(mock_update, mock_context)
    
    assert result == REQUEST_DIAGNOSIS_TIME
    assert mock_context.user_data['diagnosis_code'] == "A00"
    mock_update.message.reply_text.assert_called_once_with(
        'Please enter the registration time of the diagnosis (YYYY-MM-DD):'
    )

@pytest.mark.asyncio
async def test_request_diagnosis_code_invalid(mock_update, mock_context):
    # Подготовка
    mock_message = MagicMock(spec=Message)
    mock_message.text = "invalid"
    mock_update.message = mock_message
    mock_update.message.reply_text = AsyncMock()

    # Выполнение
    result = await request_diagnosis_code(mock_update, mock_context)

    # Проверка
    mock_update.message.reply_text.assert_called_once_with(
        'Invalid diagnosis code. Try again using this source: https://www.cito-priorov.ru/cito/files/telemed/Perechen_kodov_MKB.pdf'
    )
    assert result == REQUEST_DIAGNOSIS_CODE

@pytest.mark.asyncio
async def test_request_diagnosis_date_valid(mock_update, mock_context):
    mock_message = MagicMock(spec=Message)
    mock_message.text = "2024-03-15"
    mock_update.message = mock_message
    
    result = await request_diagnosis_date(mock_update, mock_context)
    
    assert result == REQUEST_CRYPTO_WALLET
    assert isinstance(mock_context.user_data['diagnosis_date'], date)
    mock_update.message.reply_text.assert_called_once_with(
        'Please enter the cryptowallet address principal:'
    )

@pytest.mark.asyncio
async def test_request_diagnosis_date_invalid(mock_update, mock_context):
    mock_message = MagicMock(spec=Message)
    mock_message.text = "invalid"
    mock_update.message = mock_message
    mock_update.message.reply_text = AsyncMock()
    
    result = await request_diagnosis_date(mock_update, mock_context)
    
    assert result == REQUEST_DIAGNOSIS_TIME
    mock_update.message.reply_text.assert_called_once_with(
        'Invalid date format. Please use the format YYYY-MM-DD HH:MM'
    )

@pytest.mark.asyncio
async def test_process_payout_success(
    mock_update,
    mock_context,
    mock_db_user,
    mock_insurance_company,
    mock_insurance_scheme
):
    mock_message = MagicMock(spec=Message)
    mock_update.message = mock_message
    mock_update.message.reply_text = AsyncMock()
    
    mock_context.user_data.update({
        'policy_number': '123456789',
        'diagnosis_code': 'A00',
        'diagnosis_date': date(2024, 3, 15),
        'crypto_wallet': 'test_wallet',
        'telegram_id': 12345,
        'oauth_token': 'test_token'
    })
    
    with patch('bot.handlers.request_payout_handler.db_client') as mock_db, \
         patch('bot.handlers.request_payout_handler.icp_client') as mock_icp, \
         patch('bot.handlers.request_payout_handler.get_main_menu_keyboard') as mock_keyboard:
        
        mock_db.get_user_by_telegram_id.return_value = mock_db_user
        mock_db.get_payout.return_value = None
        mock_db.get_insurance_company_by_id.return_value = mock_insurance_company
        mock_db.get_insurer_scheme.return_value = mock_insurance_scheme
        mock_icp.payout_request.return_value = True
        mock_keyboard.return_value = None
        
        result = await process_payout(mock_update, mock_context)
        
        assert result == ConversationHandler.END
        mock_db.add_payout.assert_called_once()
        mock_update.message.reply_text.assert_called_once_with(
            'Your claim is approved! 🎉\n\n',
            reply_markup=None
        )

@pytest.mark.asyncio
async def test_process_payout_invalid_date(
    mock_update,
    mock_context,
    mock_db_user
):
    mock_message = MagicMock(spec=Message)
    mock_update.message = mock_message
    mock_update.message.reply_text = AsyncMock()
    
    mock_db_user.sign_date = datetime(2024, 3, 20)
    mock_context.user_data.update({
        'policy_number': '123456789',
        'diagnosis_code': 'A00',
        'diagnosis_date': date(2024, 3, 15),
        'crypto_wallet': 'test_wallet',
        'telegram_id': 12345,
        'oauth_token': 'test_token'
    })
    
    with patch('bot.handlers.request_payout_handler.db_client') as mock_db, \
         patch('bot.handlers.request_payout_handler.get_main_menu_keyboard') as mock_keyboard:
        mock_db.get_user_by_telegram_id.return_value = mock_db_user
        mock_keyboard.return_value = None
        
        result = await process_payout(mock_update, mock_context)
        
        assert result == ConversationHandler.END
        mock_update.message.reply_text.assert_called_once_with(
            'The insured event is not relevant for the current contract by date.',
            reply_markup=None
        )

@pytest.mark.asyncio
async def test_process_payout_duplicate(
    mock_update,
    mock_context,
    mock_db_user
):
    mock_message = MagicMock(spec=Message)
    mock_update.message = mock_message
    mock_update.message.reply_text = AsyncMock()
    
    mock_context.user_data.update({
        'policy_number': '123456789',
        'diagnosis_code': 'A00',
        'diagnosis_date': date(2024, 3, 15),
        'crypto_wallet': 'test_wallet',
        'telegram_id': 12345,
        'oauth_token': 'test_token'
    })
    
    with patch('bot.handlers.request_payout_handler.db_client') as mock_db, \
         patch('bot.handlers.request_payout_handler.get_main_menu_keyboard') as mock_keyboard:
        mock_db.get_user_by_telegram_id.return_value = mock_db_user
        mock_db.get_payout.return_value = True
        mock_keyboard.return_value = None
        
        result = await process_payout(mock_update, mock_context)
        
        assert result == ConversationHandler.END
        mock_update.message.reply_text.assert_called_once_with(
            'Transfer was already made.',
            reply_markup=None
        ) 