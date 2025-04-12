import pytest
from unittest.mock import MagicMock, patch
from datetime import datetime, date
from sqlalchemy.orm import Session

from bot.clients.db_client import DBClient
from bot.models.user_info import UserInfo
from bot.models.company_info import CompanyInfo
from bot.models.insurer_scheme import InsurerScheme
from bot.models.payout import Payout

@pytest.fixture
def mock_session():
    return MagicMock(spec=Session)

@pytest.fixture
def db_client(mock_session):
    with patch('bot.clients.db_client.sessionmaker') as mock_sessionmaker:
        mock_sessionmaker.return_value.return_value = mock_session
        client = DBClient()
        return client

def test_get_user_by_email_success(db_client, mock_session):
    # Arrange
    expected_user = UserInfo(
        phone="+1234567890",
        email="test@example.com",
        insurance_amount=1000,
        payout_address="0x123",
        insurer_id=1,
        schema_version=1,
        secondary_filters=None,
        sign_date=datetime(2024, 1, 1),
        expiration_date=datetime(2024, 12, 31)
    )
    mock_session.query.return_value.filter_by.return_value.first.return_value = expected_user
    
    # Act
    result = db_client.get_user_by_email("test@example.com")
    
    # Assert
    assert result == expected_user
    mock_session.query.assert_called_once_with(UserInfo)
    mock_session.query.return_value.filter_by.assert_called_once_with(email="test@example.com")

def test_get_user_by_email_error(db_client, mock_session):
    # Arrange
    mock_session.query.side_effect = Exception("Database error")
    
    # Act
    result = db_client.get_user_by_email("test@example.com")
    
    # Assert
    assert result is None
    mock_session.close.assert_called_once()

def test_get_user_by_telegram_id_success(db_client, mock_session):
    # Arrange
    expected_user = UserInfo(
        phone="+1234567890",
        email="test@example.com",
        insurance_amount=1000,
        payout_address="0x123",
        insurer_id=1,
        schema_version=1,
        secondary_filters=None,
        sign_date=datetime(2024, 1, 1),
        expiration_date=datetime(2024, 12, 31)
    )
    mock_session.query.return_value.filter_by.return_value.first.return_value = expected_user
    
    # Act
    result = db_client.get_user_by_telegram_id(12345)
    
    # Assert
    assert result == expected_user
    mock_session.query.assert_called_once_with(UserInfo)
    mock_session.query.return_value.filter_by.assert_called_once_with(telegram_id=12345)

def test_update_user_info_success(db_client, mock_session):
    # Arrange
    user = UserInfo(
        phone="+1234567890",
        email="test@example.com",
        insurance_amount=1000,
        payout_address="0x123",
        insurer_id=1,
        schema_version=1,
        secondary_filters=None,
        sign_date=datetime(2024, 1, 1),
        expiration_date=datetime(2024, 12, 31)
    )
    
    # Act
    result = db_client.update_user_info(user)
    
    # Assert
    assert result is True
    mock_session.add.assert_called_once_with(user)
    mock_session.commit.assert_called_once()

def test_update_user_info_error(db_client, mock_session):
    # Arrange
    user = UserInfo(
        phone="+1234567890",
        email="test@example.com",
        insurance_amount=1000,
        payout_address="0x123",
        insurer_id=1,
        schema_version=1,
        secondary_filters=None,
        sign_date=datetime(2024, 1, 1),
        expiration_date=datetime(2024, 12, 31)
    )
    mock_session.commit.side_effect = Exception("Database error")
    
    # Act
    result = db_client.update_user_info(user)
    
    # Assert
    assert result is False
    mock_session.rollback.assert_called_once()

def test_get_insurer_scheme_success(db_client, mock_session):
    # Arrange
    expected_scheme = InsurerScheme(
        company_id=1,
        diagnoses_coefs='{"A01.0": 0.5}'
    )
    mock_session.query.return_value.filter_by.return_value.first.return_value = expected_scheme
    
    # Act
    result = db_client.get_insurer_scheme(1, 1)
    
    # Assert
    assert result == expected_scheme
    mock_session.query.assert_called_once_with(InsurerScheme)
    mock_session.query.return_value.filter_by.assert_called_once_with(company_id=1, global_version_num=1)

def test_get_insurance_company_by_id_success(db_client, mock_session):
    # Arrange
    expected_company = CompanyInfo(
        login="company1",
        password="secret",
        name="Test Company",
        email="company@test.com",
        pay_address="0x456"
    )
    mock_session.query.return_value.filter_by.return_value.first.return_value = expected_company
    
    # Act
    result = db_client.get_insurance_company_by_id(1)
    
    # Assert
    assert result == expected_company
    mock_session.query.assert_called_once_with(CompanyInfo)
    mock_session.query.return_value.filter_by.assert_called_once_with(id=1)

def test_get_most_popular_insurers_success(db_client, mock_session):
    # Arrange
    company1 = CompanyInfo(
        login="company1",
        password="secret",
        name="Test Company 1",
        email="company1@test.com",
        pay_address="0x456"
    )
    company2 = CompanyInfo(
        login="company2",
        password="secret",
        name="Test Company 2",
        email="company2@test.com",
        pay_address="0x789"
    )
    expected_companies = [(company1, 5), (company2, 3)]
    mock_session.query.return_value.outerjoin.return_value.group_by.return_value.order_by.return_value.limit.return_value.all.return_value = expected_companies
    
    # Act
    result = db_client.get_most_popular_insurers()
    
    # Assert
    assert result == expected_companies
    mock_session.query.assert_called_once()

def test_get_payout_success(db_client, mock_session):
    # Arrange
    expected_payout = Payout(
        transaction_id="tx123",
        amount=500,
        user_id=1,
        date=datetime(2024, 3, 15),
        company_id=1,
        diagnosis_code="A01.0",
        diagnosis_date=date(2024, 3, 15)
    )
    mock_session.query.return_value.filter_by.return_value.first.return_value = expected_payout
    
    # Act
    result = db_client.get_payout(1, "A01.0", date(2024, 3, 15))
    
    # Assert
    assert result == expected_payout
    mock_session.query.assert_called_once_with(Payout)
    mock_session.query.return_value.filter_by.assert_called_once_with(
        user_id=1,
        diagnosis_code="A01.0",
        diagnosis_date=date(2024, 3, 15)
    )

def test_add_payout_success(db_client, mock_session):
    # Arrange
    payout = Payout(
        transaction_id="tx123",
        amount=500,
        user_id=1,
        date=datetime(2024, 3, 15),
        company_id=1,
        diagnosis_code="A01.0",
        diagnosis_date=date(2024, 3, 15)
    )
    
    # Act
    result = db_client.add_payout(payout)
    
    # Assert
    assert result is True
    mock_session.add.assert_called_once_with(payout)
    mock_session.commit.assert_called_once()

def test_add_payout_error(db_client, mock_session):
    # Arrange
    payout = Payout(
        transaction_id="tx123",
        amount=500,
        user_id=1,
        date=datetime(2024, 3, 15),
        company_id=1,
        diagnosis_code="A01.0",
        diagnosis_date=date(2024, 3, 15)
    )
    mock_session.commit.side_effect = Exception("Database error")
    
    # Act
    result = db_client.add_payout(payout)
    
    # Assert
    assert result is False
    mock_session.rollback.assert_called_once() 