import pytest
from unittest.mock import patch, MagicMock
from telegram.ext import Application

from bot.main import main

@pytest.fixture
def mock_application():
    with patch('telegram.ext.Application.builder') as mock_builder:
        mock_instance = MagicMock()
        mock_builder.return_value.token.return_value.build.return_value = mock_instance
        yield mock_instance

@pytest.fixture
def mock_register_handlers():
    with patch('bot.main.register_handlers') as mock:
        yield mock

@pytest.fixture
def mock_logger():
    with patch('bot.main.logger') as mock:
        yield mock

def test_main(mock_application, mock_register_handlers, mock_logger):
    # Call main function
    main()

    # Verify application was built with token
    Application.builder.assert_called_once()
    Application.builder.return_value.token.assert_called_once()
    Application.builder.return_value.token.return_value.build.assert_called_once()

    # Verify handlers were registered
    mock_register_handlers.assert_called_once_with(application=mock_application)

    # Verify logger message
    mock_logger.info.assert_called_once_with("Bot is running!")

    # Verify polling was started
    mock_application.run_polling.assert_called_once()

def test_main():
    # Mock Application and its builder
    mock_app = MagicMock()
    mock_builder = MagicMock()
    mock_builder.token.return_value.build.return_value = mock_app
    
    # Mock get_bot_token
    mock_token = "test_token"
    
    with patch('bot.main.Application.builder', return_value=mock_builder) as mock_builder_cls, \
         patch('bot.main.get_bot_token', return_value=mock_token) as mock_get_token, \
         patch('bot.main.register_handlers') as mock_register_handlers:
        
        # Run main function
        main()
        
        # Verify bot token was requested
        mock_get_token.assert_called_once()
        
        # Verify application was built with token
        mock_builder.token.assert_called_once_with(mock_token)
        mock_builder.token.return_value.build.assert_called_once()
        
        # Verify handlers were registered
        mock_register_handlers.assert_called_once_with(application=mock_app)
        
        # Verify bot was started
        mock_app.run_polling.assert_called_once() 