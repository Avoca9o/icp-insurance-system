import pytest
from unittest.mock import patch, MagicMock

from bot.clients.mailgun_client import MailgunClient

@pytest.fixture
def mock_response():
    response = MagicMock()
    response.status_code = 200
    response.text = "Success"
    return response

@pytest.fixture
def mailgun_client():
    with patch('bot.clients.mailgun_client.MAILGUN_API_KEY', 'test_api_key'), \
         patch('bot.clients.mailgun_client.MAILGUN_DOMAIN', 'test.domain'), \
         patch('bot.clients.mailgun_client.SENDER_EMAIL', 'test@example.com'):
        return MailgunClient()

def test_send_email_success(mailgun_client, mock_response):
    # Arrange
    with patch('requests.post', return_value=mock_response) as mock_post:
        # Act
        result = mailgun_client.send_email(
            to="recipient@example.com",
            subject="Test Subject",
            text="Test Message"
        )
        
        # Assert
        assert result is True
        mock_post.assert_called_once()
        call_args = mock_post.call_args
        assert call_args[0][0] == 'https://api.mailgun.net/v3/test.domain/messages'
        assert call_args[1]['auth'] == ('api', 'test_api_key')
        assert call_args[1]['data'] == {
            'from': 'Telegram bot <test@example.com>',
            'to': ['recipient@example.com'],
            'subject': 'Test Subject',
            'text': 'Test Message'
        }

def test_send_email_failure(mailgun_client):
    # Arrange
    mock_response = MagicMock()
    mock_response.status_code = 400
    mock_response.text = "Error message"
    
    with patch('requests.post', return_value=mock_response) as mock_post, \
         patch('bot.clients.mailgun_client.logger') as mock_logger:
        # Act
        result = mailgun_client.send_email(
            to="recipient@example.com",
            subject="Test Subject",
            text="Test Message"
        )
        
        # Assert
        assert result is False
        mock_post.assert_called_once()
        mock_logger.error.assert_called_once()
        assert 'Error while sending verification code to recipient@example.com' in mock_logger.error.call_args[0][0] 