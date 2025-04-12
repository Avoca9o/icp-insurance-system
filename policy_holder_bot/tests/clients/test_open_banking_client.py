import pytest
from unittest.mock import patch, MagicMock, AsyncMock
import aiohttp

from bot.clients.open_banking_client import OpenBankingClient

@pytest.fixture
def mock_response():
    response = AsyncMock()
    response.status = 200
    response.json.return_value = {"access_token": "test_token"}
    return response

@pytest.fixture
def mock_session():
    session = AsyncMock()
    session.__aenter__.return_value = session
    session.__aexit__.return_value = None
    session.post = AsyncMock()
    session.post.return_value = AsyncMock()
    session.post.return_value.__aenter__ = AsyncMock()
    session.post.return_value.__aexit__ = AsyncMock()
    return session

@pytest.mark.asyncio
async def test_get_oauth_token_success(mock_session, mock_response):
    # Arrange
    mock_session.post.return_value.__aenter__.return_value = mock_response
    
    with patch('aiohttp.ClientSession', return_value=mock_session):
        client = OpenBankingClient()
        
        # Act
        result = await client.get_oauth_token()
        
        # Assert
        assert result == {"access_token": "test_token"}
        mock_session.post.assert_called_once()
        call_args = mock_session.post.call_args
        assert call_args[0][0].endswith('/open-data/v1.0/mfsp/token')
        assert call_args[1]['json'] == {
            'username': 'johndoe@example.com',
            'password': 'secret',
        }
        assert call_args[1]['headers'] == {
            'Content-Type': 'application/json',
        }

@pytest.mark.asyncio
async def test_get_oauth_token_error_status(mock_session):
    # Arrange
    mock_response = AsyncMock()
    mock_response.status = 400
    mock_session.post.return_value.__aenter__.return_value = mock_response
    
    with patch('aiohttp.ClientSession', return_value=mock_session):
        client = OpenBankingClient()
        
        # Act
        result = await client.get_oauth_token()
        
        # Assert
        assert result == ''

@pytest.mark.asyncio
async def test_get_oauth_token_connection_error(mock_session):
    # Arrange
    mock_session.post.side_effect = aiohttp.ClientError()
    
    with patch('aiohttp.ClientSession', return_value=mock_session):
        client = OpenBankingClient()
        
        # Act & Assert
        with pytest.raises(Exception) as exc_info:
            await client.get_oauth_token()
        assert str(exc_info.value) == 'Error while connecting to Open Banking API' 