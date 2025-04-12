import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from telegram.ext import ConversationHandler

from bot.handlers.authorization_handler import (
    authorization_handler,
    request_email,
    verify_code,
    REQUEST_EMAIL,
    REQUEST_VERIFICATION_CODE
)
from bot.models.user_info import UserInfo

@pytest.fixture
def mock_update():
    update = MagicMock()
    update.callback_query = AsyncMock()
    update.message = AsyncMock()
    update.effective_user = MagicMock()
    update.effective_user.id = 123456789
    return update

@pytest.fixture
def mock_context():
    context = MagicMock()
    context.user_data = {}
    return context

@pytest.fixture
def mock_db_client():
    with patch('bot.handlers.authorization_handler.db_client') as mock:
        mock.get_user_by_email = MagicMock()
        mock.update_user_info = MagicMock()
        yield mock

@pytest.fixture
def mock_mailgun_client():
    with patch('bot.handlers.authorization_handler.mailgun_client') as mock:
        mock.send_email = MagicMock()
        yield mock

@pytest.mark.asyncio
async def test_authorization_handler_start(mock_update, mock_context):
    # Execute
    result = await authorization_handler(mock_update, mock_context)

    # Verify
    mock_update.callback_query.answer.assert_called_once()
    mock_update.callback_query.edit_message_text.assert_called_once_with(
        'Please, enter your email address for authorization:'
    )
    assert result == REQUEST_EMAIL

@pytest.mark.asyncio
async def test_request_email_invalid_format(mock_update, mock_context):
    # Setup
    mock_update.message.text = "invalid_email"

    # Execute
    result = await request_email(mock_update, mock_context)

    # Verify
    mock_update.message.reply_text.assert_called_once_with(
        'The email you entered is not valid. Please try again.'
    )
    assert result == REQUEST_EMAIL

@pytest.mark.asyncio
async def test_request_email_user_not_found(mock_update, mock_context, mock_db_client):
    # Setup
    mock_update.message.text = "test@example.com"
    mock_db_client.get_user_by_email.return_value = None

    # Execute
    result = await request_email(mock_update, mock_context)

    # Verify
    mock_update.message.reply_text.assert_called_once_with(
        'No user was found with this email. Please try again with a different email or contact support.'
    )
    assert result == REQUEST_EMAIL

@pytest.mark.asyncio
async def test_request_email_success(mock_update, mock_context, mock_db_client, mock_mailgun_client):
    # Setup
    mock_update.message.text = "test@example.com"
    mock_db_client.get_user_by_email.return_value = UserInfo(email="test@example.com")
    mock_mailgun_client.send_email.return_value = True

    # Execute
    result = await request_email(mock_update, mock_context)

    # Verify
    mock_update.message.reply_text.assert_called_once_with(
        'We have sent a 6-digit verification code to test@example.com. Please enter it here:'
    )
    assert result == REQUEST_VERIFICATION_CODE
    assert 'verification_code' in mock_context.user_data
    assert 'attempts_left' in mock_context.user_data
    assert 'email' in mock_context.user_data
    assert mock_context.user_data['attempts_left'] == 3

@pytest.mark.asyncio
async def test_request_email_send_failure(mock_update, mock_context, mock_db_client, mock_mailgun_client):
    # Setup
    mock_update.message.text = "test@example.com"
    mock_db_client.get_user_by_email.return_value = UserInfo(email="test@example.com")
    mock_mailgun_client.send_email.return_value = False

    # Execute
    result = await request_email(mock_update, mock_context)

    # Verify
    mock_update.message.reply_text.assert_called_once_with(
        'Failed to send verification code. Please contact support. Write /start to try again'
    )
    assert result == ConversationHandler.END

@pytest.mark.asyncio
async def test_verify_code_success(mock_update, mock_context, mock_db_client):
    # Setup
    mock_update.message.text = "123456"
    mock_context.user_data['verification_code'] = "123456"
    mock_context.user_data['email'] = "test@example.com"
    mock_db_client.get_user_by_email.return_value = UserInfo(email="test@example.com")

    # Execute
    result = await verify_code(mock_update, mock_context)

    # Verify
    mock_update.message.reply_text.assert_called_once()
    call_args = mock_update.message.reply_text.call_args[0][0]
    assert 'Authorization successful!' in call_args
    assert result == ConversationHandler.END
    mock_db_client.update_user_info.assert_called_once()

@pytest.mark.asyncio
async def test_verify_code_incorrect_with_attempts(mock_update, mock_context):
    # Setup
    mock_update.message.text = "123456"
    mock_context.user_data['verification_code'] = "654321"
    mock_context.user_data['attempts_left'] = 3

    # Execute
    result = await verify_code(mock_update, mock_context)

    # Verify
    mock_update.message.reply_text.assert_called_once_with(
        'Incorrect code. Please try again. Attempts left: 2'
    )
    assert result == REQUEST_VERIFICATION_CODE
    assert mock_context.user_data['attempts_left'] == 2

@pytest.mark.asyncio
async def test_verify_code_no_attempts_left(mock_update, mock_context):
    # Setup
    mock_update.message.text = "123456"
    mock_context.user_data['verification_code'] = "654321"
    mock_context.user_data['attempts_left'] = 1

    # Execute
    result = await verify_code(mock_update, mock_context)

    # Verify
    mock_update.message.reply_text.assert_called_once_with(
        'You have exceeded the number of attempts. Please start the authorization process again via /start'
    )
    assert result == ConversationHandler.END
    assert not mock_context.user_data  # Should be cleared 