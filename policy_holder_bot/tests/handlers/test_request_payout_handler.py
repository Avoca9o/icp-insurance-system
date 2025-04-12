import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from datetime import datetime, date
from telegram.ext import ConversationHandler
import unittest.mock
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import CallbackContext

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

DIAGNOSIS_CODES = ['A01.0', 'B20.0', 'C50.0']

@pytest.fixture
def mock_update():
    update = MagicMock(spec=Update)
    update.effective_chat.id = 123
    update.effective_user.id = 456
    update.callback_query = AsyncMock()
    update.callback_query.from_user.id = 456
    update.message = AsyncMock()
    update.message.reply_text = AsyncMock()
    update.effective_message = AsyncMock()
    update.effective_message.reply_text = AsyncMock()
    return update

@pytest.fixture
def mock_context():
    context = MagicMock(spec=CallbackContext)
    context.user_data = {}
    return context

@pytest.fixture
def mock_db_client():
    client = AsyncMock()
    client.get_user_by_telegram_id = AsyncMock()
    client.get_user_info = AsyncMock()
    client.create_payout_request = AsyncMock()
    client.get_insurance_company_by_id = AsyncMock()
    client.get_insurer_scheme = AsyncMock()
    client.get_payout = AsyncMock()
    client.add_payout = AsyncMock()
    return client

@pytest.mark.asyncio
async def test_request_payout_handler_user_not_found(mock_update, mock_context, mock_db_client):
    # Arrange
    mock_db_client.get_user_by_telegram_id.return_value = None

    with patch('bot.handlers.request_payout_handler.db_client', mock_db_client), \
         patch('bot.utils.validation.DIAGNOSIS_CODES', DIAGNOSIS_CODES):
        # Act
        result = await request_payout_handler(mock_update, mock_context)
        
        # Assert
        mock_update.callback_query.edit_message_text.assert_called_once_with(
            'You are not authorized. Please authorize using the /start command.'
        )
        assert result == ConversationHandler.END

@pytest.mark.asyncio
async def test_request_payout_handler_not_approved(mock_update, mock_context, mock_db_client):
    # Arrange
    mock_user = MagicMock()
    mock_user.is_approved = False
    mock_db_client.get_user_by_telegram_id.return_value = mock_user

    with patch('bot.handlers.request_payout_handler.db_client', mock_db_client), \
         patch('bot.utils.validation.DIAGNOSIS_CODES', DIAGNOSIS_CODES):
        # Act
        result = await request_payout_handler(mock_update, mock_context)
        
        # Assert
        mock_update.callback_query.edit_message_text.assert_called_once_with(
            'Your contract information is not approved yet. Please confirm your information before requesting a payout.',
            reply_markup=mock_update.callback_query.edit_message_text.call_args[1]['reply_markup']
        )
        assert result == ConversationHandler.END

@pytest.mark.asyncio
async def test_request_payout_handler_success(mock_update, mock_context, mock_db_client):
    # Arrange
    mock_user = MagicMock()
    mock_user.is_approved = True
    mock_db_client.get_user_by_telegram_id.return_value = AsyncMock(return_value=mock_user)

    with patch('bot.handlers.request_payout_handler.db_client', mock_db_client), \
         patch('bot.utils.validation.DIAGNOSIS_CODES', DIAGNOSIS_CODES):
        # Act
        result = await request_payout_handler(mock_update, mock_context)
        
        # Assert
        mock_update.callback_query.edit_message_text.assert_called_once_with(
            'To process payout request, please confirm that you provide access to your personal information:',
            reply_markup=mock_update.callback_query.edit_message_text.call_args[1]['reply_markup']
        )
        assert result == APPROVE_ACCESS

@pytest.mark.asyncio
async def test_approve_access_confirm(mock_update, mock_context, mock_open_banking_client):
    # Arrange
    mock_update.callback_query.data = 'confirm_personal_data'
    
    with patch('bot.handlers.request_payout_handler.open_banking_client', mock_open_banking_client), \
         patch('bot.utils.validation.DIAGNOSIS_CODES', DIAGNOSIS_CODES):
        # Act
        result = await approve_access(mock_update, mock_context)
        
        # Assert
        assert result == REQUEST_POLICY_NUMBER
        mock_update.callback_query.edit_message_text.assert_called_once()
        assert 'Personal data access confirmed' in mock_update.callback_query.edit_message_text.call_args[0][0]

@pytest.mark.asyncio
async def test_approve_access_cancel(mock_update, mock_context):
    # Arrange
    mock_update.callback_query.data = 'cancel'
    
    with patch('bot.utils.validation.DIAGNOSIS_CODES', DIAGNOSIS_CODES):
        # Act
        result = await approve_access(mock_update, mock_context)
        
        # Assert
        assert result == ConversationHandler.END
        mock_update.callback_query.edit_message_text.assert_called_once()
        assert 'Payout request canceled' in mock_update.callback_query.edit_message_text.call_args[0][0]

@pytest.mark.asyncio
async def test_request_policy_number_invalid(mock_update, mock_context):
    # Arrange
    mock_update.message.text = "invalid"
    
    with patch('bot.utils.validation.DIAGNOSIS_CODES', DIAGNOSIS_CODES):
        # Act
        result = await request_policy_number(mock_update, mock_context)
        
        # Assert
        assert mock_update.message.reply_text.call_count == 1
        assert 'Invalid policy number' in mock_update.message.reply_text.call_args_list[0][0][0]
        assert result == ConversationHandler.END

@pytest.mark.asyncio
async def test_request_policy_number_valid(mock_update, mock_context):
    # Arrange
    mock_update.message.text = "123456789"
    
    with patch('bot.utils.validation.DIAGNOSIS_CODES', DIAGNOSIS_CODES):
        # Act
        result = await request_policy_number(mock_update, mock_context)
        
        # Assert
        assert result == REQUEST_DIAGNOSIS_CODE
        mock_context.user_data['policy_number'] = "123456789"
        mock_update.message.reply_text.assert_called_once_with('Please enter the diagnosis code:')

@pytest.mark.asyncio
async def test_request_diagnosis_code_invalid(mock_update, mock_context):
    # Arrange
    mock_update.message.text = "invalid"
    
    with patch('bot.utils.validation.DIAGNOSIS_CODES', DIAGNOSIS_CODES):
        # Act
        result = await request_diagnosis_code(mock_update, mock_context)
        
        # Assert
        assert mock_update.message.reply_text.call_count == 1
        assert 'Invalid diagnosis code' in mock_update.message.reply_text.call_args_list[0][0][0]
        assert result == ConversationHandler.END

@pytest.mark.asyncio
async def test_request_diagnosis_code_valid(mock_update, mock_context):
    # Arrange
    mock_update.message.text = "A01.0"
    
    with patch('bot.utils.validation.DIAGNOSIS_CODES', DIAGNOSIS_CODES):
        # Act
        result = await request_diagnosis_code(mock_update, mock_context)
        
        # Assert
        assert result == REQUEST_DIAGNOSIS_TIME
        mock_context.user_data['diagnosis_code'] = "A01.0"
        mock_update.message.reply_text.assert_called_once_with('Please enter the registration time of the diagnosis (YYYY-MM-DD):')

@pytest.mark.asyncio
async def test_request_diagnosis_date_invalid(mock_update, mock_context):
    # Arrange
    mock_update.message.text = "invalid"

    with patch('bot.utils.validation.DIAGNOSIS_CODES', DIAGNOSIS_CODES):
        # Act
        result = await request_diagnosis_date(mock_update, mock_context)

        # Assert
        assert result == ConversationHandler.END
        assert mock_update.message.reply_text.call_count == 1
        assert 'Invalid date format' in mock_update.message.reply_text.call_args_list[0][0][0]

@pytest.mark.asyncio
async def test_request_diagnosis_date_valid(mock_update, mock_context):
    # Arrange
    mock_update.message.text = "2024-03-20"
    
    with patch('bot.utils.validation.DIAGNOSIS_CODES', DIAGNOSIS_CODES):
        # Act
        result = await request_diagnosis_date(mock_update, mock_context)
        
        # Assert
        assert result == REQUEST_CRYPTO_WALLET
        assert isinstance(mock_context.user_data['diagnosis_date'], date)
        mock_update.message.reply_text.assert_called_once_with('Please enter the cryptowallet address principal:')

@pytest.mark.asyncio
async def test_process_payout_success(mock_update, mock_context, mock_db_client, mock_icp_client):
    # Arrange
    mock_user = MagicMock()
    mock_user.id = 1
    mock_user.sign_date = datetime(2024, 1, 1)
    mock_user.expiration_date = datetime(2024, 12, 31)
    mock_user.insurance_amount = 1000
    mock_user.insurer_id = 1
    mock_user.schema_version = 1
    mock_user.secondary_filters = None

    mock_db_client.get_user_by_telegram_id.return_value = mock_user
    mock_db_client.get_payout.return_value = None
    mock_db_client.get_insurer_scheme.return_value = MagicMock(diagnoses_coefs='{"A01.0": 0.5}')
    mock_db_client.get_insurance_company_by_id.return_value = MagicMock(pay_address="wallet123")
    mock_icp_client.payout_request = AsyncMock(return_value=True)

    mock_context.user_data = {
        'policy_number': '123456789',
        'diagnosis_code': 'A01.0',
        'diagnosis_date': date(2024, 3, 20),
        'crypto_wallet': 'user_wallet123',
        'telegram_id': 456,
        'oauth_token': 'token123'
    }

    with patch('bot.handlers.request_payout_handler.db_client', mock_db_client), \
         patch('bot.handlers.request_payout_handler.icp_client', mock_icp_client), \
         patch('bot.utils.validation.DIAGNOSIS_CODES', DIAGNOSIS_CODES):
        # Act
        result = await process_payout(mock_update, mock_context)

        # Assert
        assert result == ConversationHandler.END
        mock_update.message.reply_text.assert_called_once_with(
            'Your claim is approved! 🎉\n\n',
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text='🔘 Main Menu', callback_data='main_menu')]])
        )

@pytest.mark.asyncio
async def test_process_payout_date_out_of_range(mock_update, mock_context, mock_db_client):
    # Arrange
    mock_user = MagicMock()
    mock_user.id = 1
    mock_user.sign_date = datetime(2024, 4, 1)
    mock_user.expiration_date = datetime(2024, 12, 31)

    mock_db_client.get_user_by_telegram_id.return_value = mock_user

    mock_context.user_data = {
        'policy_number': '123456789',
        'diagnosis_code': 'A01.0',
        'diagnosis_date': date(2024, 3, 20),
        'telegram_id': 456
    }

    with patch('bot.handlers.request_payout_handler.db_client', mock_db_client), \
         patch('bot.utils.validation.DIAGNOSIS_CODES', DIAGNOSIS_CODES):
        # Act
        result = await process_payout(mock_update, mock_context)

        # Assert
        assert result == ConversationHandler.END
        mock_update.message.reply_text.assert_called_once_with(
            'The insured event is not relevant for the current contract by date.',
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text='🔘 Main Menu', callback_data='main_menu')]])
        )

@pytest.mark.asyncio
async def test_process_payout_already_processed(mock_update, mock_context, mock_db_client):
    # Arrange
    mock_user = MagicMock()
    mock_user.id = 1
    mock_user.sign_date = datetime(2024, 1, 1)
    mock_user.expiration_date = datetime(2024, 12, 31)

    mock_db_client.get_user_by_telegram_id.return_value = mock_user
    mock_db_client.get_payout.return_value = MagicMock()

    mock_context.user_data = {
        'policy_number': '123456789',
        'diagnosis_code': 'A01.0',
        'diagnosis_date': date(2024, 3, 20),
        'telegram_id': 456
    }

    with patch('bot.handlers.request_payout_handler.db_client', mock_db_client), \
         patch('bot.utils.validation.DIAGNOSIS_CODES', DIAGNOSIS_CODES):
        # Act
        result = await process_payout(mock_update, mock_context)

        # Assert
        assert result == ConversationHandler.END
        mock_update.message.reply_text.assert_called_once_with(
            'Transfer was already made.',
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text='🔘 Main Menu', callback_data='main_menu')]])
        )

@pytest.mark.asyncio
async def test_request_payout_handler_error(mock_update, mock_context, mock_db_client):
    # Mock db_client to raise an exception
    mock_db_client.get_user_by_telegram_id.side_effect = Exception("Database error")

    with patch('bot.handlers.request_payout_handler.db_client', mock_db_client), \
         patch('bot.utils.validation.DIAGNOSIS_CODES', DIAGNOSIS_CODES):
        # Act
        result = await request_payout_handler(mock_update, mock_context)

        # Assert
        mock_update.callback_query.edit_message_text.assert_called_once_with(
            'An error occurred while processing your request. Please try again later.',
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text='🔘 Main Menu', callback_data='main_menu')]])
        )

@pytest.mark.asyncio
async def test_request_diagnosis_code_not_found(mock_update, mock_context):
    # Set up valid but non-existent diagnosis code
    mock_update.message.text = "Z99.9"

    with patch('bot.utils.validation.DIAGNOSIS_CODES', DIAGNOSIS_CODES):
        # Act
        result = await request_diagnosis_code(mock_update, mock_context)

        # Assert
        assert result == REQUEST_DIAGNOSIS_TIME
        mock_update.message.reply_text.assert_called_once_with('Please enter the registration time of the diagnosis (YYYY-MM-DD):')

@pytest.mark.asyncio
async def test_request_crypto_wallet_error(mock_update, mock_context, mock_db_client):
    # Set up wallet address and user data
    mock_update.message.text = "invalid_wallet"
    mock_context.user_data = {
        'policy_number': '123456789',
        'diagnosis_code': 'A01.0',
        'diagnosis_date': date(2024, 3, 20),
        'telegram_id': 456,
        'oauth_token': 'token123'
    }

    mock_user = MagicMock()
    mock_user.id = 1
    mock_user.sign_date = datetime(2024, 1, 1)
    mock_user.expiration_date = datetime(2024, 12, 31)
    mock_user.insurance_amount = 1000
    mock_user.insurer_id = 1
    mock_user.schema_version = 1
    mock_user.secondary_filters = None

    mock_db_client.get_user_by_telegram_id.return_value = mock_user
    mock_db_client.get_payout.return_value = None
    mock_db_client.get_insurer_scheme.return_value = MagicMock(diagnoses_coefs='{"A01.0": 0.5}')
    mock_db_client.get_insurance_company_by_id.return_value = MagicMock(pay_address="wallet123")

    with patch('bot.handlers.request_payout_handler.db_client', mock_db_client), \
         patch('bot.utils.validation.DIAGNOSIS_CODES', DIAGNOSIS_CODES):
        # Act
        result = await request_crypto_wallet(mock_update, mock_context)

        # Assert
        assert result == ConversationHandler.END
        mock_update.message.reply_text.assert_called_with(
            'An error occurred while processing your request. Please try again later.',
            reply_markup=mock_update.message.reply_text.call_args[1]['reply_markup']
        ) 