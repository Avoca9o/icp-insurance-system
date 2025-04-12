import pytest
from unittest.mock import MagicMock, patch
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ConversationHandler, MessageHandler, filters

from bot.utils.register_handlers import register_handlers

@pytest.fixture
def mock_application():
    return MagicMock(spec=Application)

@pytest.fixture
def mock_handlers():
    with patch('bot.utils.register_handlers.start_handler') as mock_start, \
         patch('bot.utils.register_handlers.help_handler') as mock_help, \
         patch('bot.utils.register_handlers.authorization_handler') as mock_auth, \
         patch('bot.utils.register_handlers.request_email') as mock_request_email, \
         patch('bot.utils.register_handlers.verify_code') as mock_verify_code, \
         patch('bot.utils.register_handlers.cancel_authorization_handler') as mock_cancel_auth, \
         patch('bot.utils.register_handlers.insurers_list_handler') as mock_insurers, \
         patch('bot.utils.register_handlers.main_menu_handler') as mock_main_menu, \
         patch('bot.utils.register_handlers.approve_contract_handler') as mock_approve, \
         patch('bot.utils.register_handlers.view_contract_handler') as mock_view, \
         patch('bot.utils.register_handlers.request_payout_handler') as mock_payout, \
         patch('bot.utils.register_handlers.approve_access') as mock_approve_access, \
         patch('bot.utils.register_handlers.request_policy_number') as mock_policy, \
         patch('bot.utils.register_handlers.request_diagnosis_code') as mock_diagnosis, \
         patch('bot.utils.register_handlers.request_diagnosis_date') as mock_date, \
         patch('bot.utils.register_handlers.request_crypto_wallet') as mock_wallet, \
         patch('bot.utils.register_handlers.cancel_payout_handler') as mock_cancel_payout:
        
        yield {
            'start': mock_start,
            'help': mock_help,
            'auth': mock_auth,
            'request_email': mock_request_email,
            'verify_code': mock_verify_code,
            'cancel_auth': mock_cancel_auth,
            'insurers': mock_insurers,
            'main_menu': mock_main_menu,
            'approve': mock_approve,
            'view': mock_view,
            'payout': mock_payout,
            'approve_access': mock_approve_access,
            'policy': mock_policy,
            'diagnosis': mock_diagnosis,
            'date': mock_date,
            'wallet': mock_wallet,
            'cancel_payout': mock_cancel_payout
        }

def test_register_handlers(mock_application, mock_handlers):
    register_handlers(mock_application)

    # Get all calls to add_handler
    calls = mock_application.add_handler.call_args_list

    # Verify command handlers were registered
    command_handlers = [
        call.args[0] for call in calls 
        if isinstance(call.args[0], CommandHandler)
    ]
    assert any(
        'start' in handler.commands and handler.callback == mock_handlers['start']
        for handler in command_handlers
    )
    assert any(
        'help' in handler.commands and handler.callback == mock_handlers['help']
        for handler in command_handlers
    )

    # Verify callback query handlers were registered
    callback_handlers = [
        call.args[0] for call in calls 
        if isinstance(call.args[0], CallbackQueryHandler) and not isinstance(call.args[0], ConversationHandler)
    ]

    # Helper function to check handler pattern and callback
    def find_handler_with_pattern_and_callback(pattern, expected_callback):
        return any(
            handler.pattern.pattern == pattern and handler.callback == expected_callback
            for handler in callback_handlers
        )

    # Verify each callback query handler
    assert find_handler_with_pattern_and_callback('^insurers_list$', mock_handlers['insurers'])
    assert find_handler_with_pattern_and_callback('^main_menu$', mock_handlers['main_menu'])
    assert find_handler_with_pattern_and_callback('^approve_contract$', mock_handlers['approve'])
    assert find_handler_with_pattern_and_callback('^view_contract$', mock_handlers['view'])

    # Verify conversation handlers were added
    conversation_handlers = [
        call.args[0] for call in calls 
        if isinstance(call.args[0], ConversationHandler)
    ]
    assert len(conversation_handlers) == 2  # Authorization and payout handlers 