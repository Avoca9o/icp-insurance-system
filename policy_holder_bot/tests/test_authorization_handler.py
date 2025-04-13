import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from telegram import Update, CallbackQuery, Message, User
from telegram.ext import ContextTypes, ConversationHandler

from bot.handlers.authorization_handler import (
    authorization_handler,
    email_handler,
    verify_code,
    REQUEST_EMAIL,
    REQUEST_VERIFICATION_CODE
)
from bot.models.user_info import UserInfo

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
    with patch('bot.handlers.authorization_handler.db_client') as mock:
        yield mock

@pytest.fixture
def mock_mailgun_client():
    with patch('bot.handlers.authorization_handler.mailgun_client') as mock:
        yield mock

@pytest.mark.asyncio
async def test_authorization_handler(mock_update, mock_context):
    # Подготовка
    mock_update.callback_query = AsyncMock(spec=CallbackQuery)
    mock_update.callback_query.answer = AsyncMock()
    mock_update.callback_query.edit_message_text = AsyncMock()

    # Выполнение
    result = await authorization_handler(mock_update, mock_context)

    # Проверка
    mock_update.callback_query.answer.assert_called_once()
    mock_update.callback_query.edit_message_text.assert_called_once_with(
        'Please, enter your email address for authorization:'
    )
    assert result == REQUEST_EMAIL

@pytest.mark.asyncio
async def test_email_handler_invalid_email(mock_update, mock_context):
    # Подготовка
    mock_update.message = AsyncMock(spec=Message)
    mock_update.message.text = "invalid_email"
    mock_update.message.reply_text = AsyncMock()

    # Выполнение
    result = await email_handler(mock_update, mock_context)

    # Проверка
    mock_update.message.reply_text.assert_called_once_with(
        'The email you entered is not valid. Please try again.'
    )
    assert result == REQUEST_EMAIL

@pytest.mark.asyncio
async def test_email_handler_user_not_found(mock_update, mock_context, mock_db_client):
    # Подготовка
    mock_update.message = AsyncMock(spec=Message)
    mock_update.message.text = "test@example.com"
    mock_update.message.reply_text = AsyncMock()
    mock_db_client.get_user_by_email.return_value = None

    # Выполнение
    result = await email_handler(mock_update, mock_context)

    # Проверка
    mock_update.message.reply_text.assert_called_once_with(
        'No user was found with this email. Please try again with a different email or contact support.'
    )
    assert result == REQUEST_EMAIL

@pytest.mark.asyncio
async def test_email_handler_success(mock_update, mock_context, mock_db_client, mock_mailgun_client):
    # Подготовка
    mock_update.message = AsyncMock(spec=Message)
    mock_update.message.text = "test@example.com"
    mock_update.message.reply_text = AsyncMock()

    mock_user = MagicMock(spec=UserInfo)
    mock_db_client.get_user_by_email.return_value = mock_user
    mock_mailgun_client.send_email.return_value = True

    # Выполнение
    result = await email_handler(mock_update, mock_context)

    # Проверка
    mock_update.message.reply_text.assert_called_once()
    assert 'verification code' in mock_update.message.reply_text.call_args[0][0]
    assert result == REQUEST_VERIFICATION_CODE
    assert 'verification_code' in mock_context.user_data
    assert 'attempts_left' in mock_context.user_data
    assert mock_context.user_data['attempts_left'] == 3
    assert mock_context.user_data['email'] == "test@example.com"

@pytest.mark.asyncio
async def test_email_handler_send_email_failed(mock_update, mock_context, mock_db_client, mock_mailgun_client):
    # Подготовка
    mock_update.message = AsyncMock(spec=Message)
    mock_update.message.text = "test@example.com"
    mock_update.message.reply_text = AsyncMock()

    mock_user = MagicMock(spec=UserInfo)
    mock_db_client.get_user_by_email.return_value = mock_user
    mock_mailgun_client.send_email.return_value = False

    # Выполнение
    result = await email_handler(mock_update, mock_context)

    # Проверка
    mock_update.message.reply_text.assert_called_once_with(
        'Failed to send verification code. Please contact support. Write /start to try again'
    )
    assert result == ConversationHandler.END

@pytest.mark.asyncio
async def test_verify_code_success(mock_update, mock_context, mock_db_client):
    # Подготовка
    mock_update.message = AsyncMock(spec=Message)
    mock_update.message.text = "123456"
    mock_update.message.reply_text = AsyncMock()

    mock_context.user_data = {
        'verification_code': '123456',
        'email': 'test@example.com',
        'attempts_left': 3
    }

    mock_user = MagicMock(spec=UserInfo)
    mock_db_client.get_user_by_email.return_value = mock_user

    # Выполнение
    result = await verify_code(mock_update, mock_context)

    # Проверка
    mock_update.message.reply_text.assert_called_once()
    assert 'Authorization successful!' in mock_update.message.reply_text.call_args[0][0]
    assert result == ConversationHandler.END
    assert mock_user.telegram_id == mock_update.effective_user.id
    mock_db_client.update_user_info.assert_called_once_with(mock_user)

@pytest.mark.asyncio
async def test_verify_code_incorrect_with_attempts(mock_update, mock_context):
    # Подготовка
    mock_update.message = AsyncMock(spec=Message)
    mock_update.message.text = "654321"
    mock_update.message.reply_text = AsyncMock()

    mock_context.user_data = {
        'verification_code': '123456',
        'attempts_left': 3
    }

    # Выполнение
    result = await verify_code(mock_update, mock_context)

    # Проверка
    mock_update.message.reply_text.assert_called_once()
    assert 'Incorrect code' in mock_update.message.reply_text.call_args[0][0]
    assert result == REQUEST_VERIFICATION_CODE
    assert mock_context.user_data['attempts_left'] == 2

@pytest.mark.asyncio
async def test_verify_code_no_attempts_left(mock_update, mock_context):
    # Подготовка
    mock_update.message = AsyncMock(spec=Message)
    mock_update.message.text = "654321"
    mock_update.message.reply_text = AsyncMock()

    mock_context.user_data = {
        'verification_code': '123456',
        'attempts_left': 1
    }

    # Выполнение
    result = await verify_code(mock_update, mock_context)

    # Проверка
    mock_update.message.reply_text.assert_called_once_with(
        'You have exceeded the number of attempts. Please start the authorization process again via /start'
    )
    assert result == ConversationHandler.END
    assert not mock_context.user_data  # user_data должен быть очищен 