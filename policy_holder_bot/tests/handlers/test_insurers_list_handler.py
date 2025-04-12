import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from bot.handlers.insurers_list_handler import insurers_list_handler
from bot.models.insurance_company import InsuranceCompany

@pytest.fixture
def mock_update():
    update = MagicMock()
    update.callback_query = AsyncMock()
    update.callback_query.edit_message_text = AsyncMock()
    return update

@pytest.fixture
def mock_context():
    return MagicMock()

@pytest.fixture
def mock_db_client():
    with patch('bot.handlers.insurers_list_handler.db_client') as mock:
        mock.get_most_popular_insurers = MagicMock()
        yield mock

@pytest.mark.asyncio
async def test_insurers_list_handler_with_companies(mock_update, mock_context, mock_db_client):
    # Setup
    companies = [
        (InsuranceCompany(name="Company A", email="a@example.com"), 10),
        (InsuranceCompany(name="Company B", email="b@example.com"), 5),
    ]
    mock_db_client.get_most_popular_insurers.return_value = companies

    # Execute
    await insurers_list_handler(mock_update, mock_context)

    # Verify
    mock_update.callback_query.answer.assert_called_once()
    mock_update.callback_query.edit_message_text.assert_called_once()
    call_args = mock_update.callback_query.edit_message_text.call_args[0][0]
    assert 'Below are the most popular companies among users:' in call_args
    assert 'Company A' in call_args
    assert 'a@example.com' in call_args
    assert '10' in call_args
    assert 'Company B' in call_args
    assert 'b@example.com' in call_args
    assert '5' in call_args

@pytest.mark.asyncio
async def test_insurers_list_handler_empty(mock_update, mock_context, mock_db_client):
    # Setup
    mock_db_client.get_most_popular_insurers.return_value = []

    # Execute
    await insurers_list_handler(mock_update, mock_context)

    # Verify
    mock_update.callback_query.answer.assert_called_once()
    mock_update.callback_query.edit_message_text.assert_called_once()
    call_args = mock_update.callback_query.edit_message_text.call_args[0][0]
    assert 'Below are the most popular companies among users:' in call_args
    assert 'To log in, click on' in call_args 