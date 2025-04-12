import pytest
from unittest.mock import MagicMock, patch
from datetime import date

from bot.clients.icp_client import ICPClient

@pytest.fixture
def mock_canister():
    return MagicMock()

@pytest.fixture
def icp_client(mock_canister):
    with patch('bot.clients.icp_client.Canister') as mock_canister_class:
        mock_canister_class.return_value = mock_canister
        client = ICPClient()
        return client

def test_add_approved_client_success(icp_client, mock_canister):
    # Arrange
    mock_canister.add_approved_client.return_value = True
    
    # Act
    result = icp_client.add_approved_client(
        insurer_wallet_address="wallet123",
        policy_holder_id=1,
        checksum="checksum123"
    )
    
    # Assert
    assert result is True
    mock_canister.add_approved_client.assert_called_once_with(
        "wallet123",
        1,
        "checksum123"
    )

def test_add_approved_client_failure(icp_client, mock_canister):
    # Arrange
    mock_canister.add_approved_client.return_value = False
    
    # Act
    result = icp_client.add_approved_client(
        insurer_wallet_address="wallet123",
        policy_holder_id=1,
        checksum="checksum123"
    )
    
    # Assert
    assert result is False
    mock_canister.add_approved_client.assert_called_once_with(
        "wallet123",
        1,
        "checksum123"
    )

def test_payout_request_success(icp_client, mock_canister):
    # Arrange
    mock_canister.request_payout.return_value = "Transfer was approved"
    
    # Act
    result = icp_client.payout_request(
        amount=1000,
        policy_number="123456789",
        diagnosis_code="A01.0",
        diagnosis_date=date(2024, 3, 15),
        crypto_wallet="wallet123",
        insurer_crypto_wallet="insurer_wallet123",
        oauth_token="token123"
    )
    
    # Assert
    assert result is True
    mock_canister.request_payout.assert_called_once_with(
        "123456789",
        "A01.0",
        "2024-03-15",
        "insurer_wallet123",
        "wallet123",
        1000,
        "token123"
    )

def test_payout_request_failure(icp_client, mock_canister):
    # Arrange
    mock_canister.request_payout.return_value = "Transfer was denied"
    
    # Act
    result = icp_client.payout_request(
        amount=1000,
        policy_number="123456789",
        diagnosis_code="A01.0",
        diagnosis_date=date(2024, 3, 15),
        crypto_wallet="wallet123",
        insurer_crypto_wallet="insurer_wallet123",
        oauth_token="token123"
    )
    
    # Assert
    assert result is False
    mock_canister.request_payout.assert_called_once_with(
        "123456789",
        "A01.0",
        "2024-03-15",
        "insurer_wallet123",
        "wallet123",
        1000,
        "token123"
    ) 