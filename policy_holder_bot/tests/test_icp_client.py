import pytest
from unittest.mock import Mock, patch
from datetime import date
from bot.clients.icp_client import ICPClient

@pytest.fixture
def mock_canister():
    return Mock()

@pytest.fixture
def icp_client(mock_canister):
    with patch('bot.clients.icp_client.Identity'), \
         patch('bot.clients.icp_client.Client'), \
         patch('bot.clients.icp_client.Agent'), \
         patch('bot.clients.icp_client.Canister', return_value=mock_canister):
        client = ICPClient()
        client.canister = mock_canister
        return client

def test_initialization(icp_client):
    """Тест инициализации ICPClient"""
    assert icp_client.canister is not None

def test_add_approved_client_success(icp_client):
    """Тест успешного добавления одобренного клиента"""
    # Подготовка
    insurer_wallet = "test_wallet"
    policy_holder_id = 123
    checksum = "test_checksum"
    icp_client.canister.add_approved_client.return_value = True

    # Действие
    result = icp_client.add_approved_client(
        insurer_wallet,
        policy_holder_id,
        checksum
    )

    # Проверка
    assert result is True
    icp_client.canister.add_approved_client.assert_called_once_with(
        insurer_wallet, policy_holder_id, checksum
    )

def test_add_approved_client_failure(icp_client):
    """Тест неудачного добавления одобренного клиента"""
    # Подготовка
    insurer_wallet = "test_wallet"
    policy_holder_id = 123
    checksum = "test_checksum"
    icp_client.canister.add_approved_client.return_value = False

    # Действие
    result = icp_client.add_approved_client(
        insurer_wallet,
        policy_holder_id,
        checksum
    )

    # Проверка
    assert result is False
    icp_client.canister.add_approved_client.assert_called_once_with(
        insurer_wallet, policy_holder_id, checksum
    )

def test_payout_request_success(icp_client):
    """Тест успешного запроса выплаты"""
    # Подготовка
    amount = 1000
    policy_number = "POL123"
    diagnosis_code = "A00"
    diagnosis_date = date(2024, 3, 15)
    crypto_wallet = "holder_wallet"
    insurer_crypto_wallet = "insurer_wallet"
    oauth_token = "test_token"
    icp_client.canister.request_payout.return_value = "Payout successful"

    # Действие
    result = icp_client.payout_request(
        amount,
        policy_number,
        diagnosis_code,
        diagnosis_date,
        crypto_wallet,
        insurer_crypto_wallet,
        oauth_token
    )

    # Проверка
    assert result is True
    icp_client.canister.request_payout.assert_called_once_with(
        policy_number,
        diagnosis_code,
        str(diagnosis_date),
        insurer_crypto_wallet,
        crypto_wallet,
        amount,
        oauth_token
    )

def test_payout_request_failure(icp_client):
    """Тест неудачного запроса выплаты"""
    # Подготовка
    amount = 1000
    policy_number = "POL123"
    diagnosis_code = "A00"
    diagnosis_date = date(2024, 3, 15)
    crypto_wallet = "holder_wallet"
    insurer_crypto_wallet = "insurer_wallet"
    oauth_token = "test_token"
    icp_client.canister.request_payout.return_value = "Payout failed"

    # Действие
    result = icp_client.payout_request(
        amount,
        policy_number,
        diagnosis_code,
        diagnosis_date,
        crypto_wallet,
        insurer_crypto_wallet,
        oauth_token
    )

    # Проверка
    assert result is False
    icp_client.canister.request_payout.assert_called_once_with(
        policy_number,
        diagnosis_code,
        str(diagnosis_date),
        insurer_crypto_wallet,
        crypto_wallet,
        amount,
        oauth_token
    ) 