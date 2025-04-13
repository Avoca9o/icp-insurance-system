import pytest
from unittest.mock import AsyncMock, MagicMock
from datetime import datetime
from tests.utils import get_main_menu_keyboard
from telegram import Message
from telegram.ext import ConversationHandler

@pytest.mark.asyncio
async def test_request_crypto_wallet(mock_update, mock_context, mock_db_client):
    mock_update.message = AsyncMock(spec=Message)
    mock_update.message.text = "test_wallet"
    mock_update.message.reply_text = AsyncMock()
    mock_context.user_data = {
        'policy_number': '123456789',
        'diagnosis_code': 'A00',
        'diagnosis_date': '2024-01-01',
        'telegram_id': 123456789,
        'oauth_token': 'test_token'
    }

    mock_user = MagicMock()
    mock_user.sign_date = datetime(2023, 1, 1)
    mock_user.expiration_date = datetime(2025, 1, 1)
    mock_user.id = 1
    mock_user.insurer_id = 1
    mock_user.insurance_amount = 1000
    mock_user.secondary_filters = None
    mock_db_client.get_user_by_telegram_id.return_value = mock_user

    mock_insurer_scheme = MagicMock()
    mock_insurer_scheme.diagnoses_coefs = '{"A00": 0.5}'
    mock_db_client.get_insurer_scheme.return_value = mock_insurer_scheme

    mock_insurance_company = MagicMock()
    mock_insurance_company.pay_address = 'test_address'
    mock_db_client.get_insurance_company_by_id.return_value = mock_insurance_company

    mock_db_client.get_payout.return_value = True  # Simulate existing payout

    result = await request_crypto_wallet(mock_update, mock_context)

    assert mock_context.user_data['crypto_wallet'] == "test_wallet"
    mock_update.message.reply_text.assert_called_once_with(
        'Transfer was already made.',
        reply_markup=get_main_menu_keyboard()
    )
    assert result == ConversationHandler.END 