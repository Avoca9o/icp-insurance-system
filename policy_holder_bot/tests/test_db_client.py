import pytest
from datetime import datetime, date
from unittest.mock import MagicMock, patch
from sqlalchemy.orm import Session

from bot.clients.db_client import DBClient
from bot.models.user_info import UserInfo
from bot.models.company_info import CompanyInfo
from bot.models.insurer_scheme import InsurerScheme
from bot.models.payout import Payout

@pytest.fixture
def mock_session():
    with patch('bot.clients.db_client.sessionmaker') as mock_sessionmaker:
        mock_session = MagicMock(spec=Session)
        mock_sessionmaker.return_value = lambda: mock_session
        yield mock_session

@pytest.fixture
def db_client(mock_session):
    with patch('bot.clients.db_client.create_engine'), \
         patch('bot.clients.db_client.Base.metadata.create_all'):
        return DBClient()

def test_get_user_by_email(db_client, mock_session):
    # Подготовка
    mock_user = MagicMock(spec=UserInfo)
    mock_session.query.return_value.filter_by.return_value.first.return_value = mock_user

    # Выполнение
    result = db_client.get_user_by_email('test@example.com')

    # Проверка
    assert result == mock_user
    mock_session.query.assert_called_once_with(UserInfo)
    mock_session.query.return_value.filter_by.assert_called_once_with(email='test@example.com')
    mock_session.close.assert_called_once()

def test_get_user_by_email_exception(db_client, mock_session):
    # Подготовка
    mock_session.query.side_effect = Exception('Database error')

    # Выполнение
    result = db_client.get_user_by_email('test@example.com')

    # Проверка
    assert result is None
    mock_session.close.assert_called_once()

def test_get_user_by_telegram_id(db_client, mock_session):
    # Подготовка
    mock_user = MagicMock(spec=UserInfo)
    mock_session.query.return_value.filter_by.return_value.first.return_value = mock_user

    # Выполнение
    result = db_client.get_user_by_telegram_id(123456789)

    # Проверка
    assert result == mock_user
    mock_session.query.assert_called_once_with(UserInfo)
    mock_session.query.return_value.filter_by.assert_called_once_with(telegram_id=123456789)
    mock_session.close.assert_called_once()

def test_update_user_info_success(db_client, mock_session):
    # Подготовка
    mock_user = MagicMock(spec=UserInfo)

    # Выполнение
    result = db_client.update_user_info(mock_user)

    # Проверка
    assert result is True
    mock_session.add.assert_called_once_with(mock_user)
    mock_session.commit.assert_called_once()
    mock_session.close.assert_called_once()

def test_update_user_info_failure(db_client, mock_session):
    # Подготовка
    mock_user = MagicMock(spec=UserInfo)
    mock_session.commit.side_effect = Exception('Database error')

    # Выполнение
    result = db_client.update_user_info(mock_user)

    # Проверка
    assert result is False
    mock_session.add.assert_called_once_with(mock_user)
    mock_session.rollback.assert_called_once()
    mock_session.close.assert_called_once()

def test_get_insurer_scheme(db_client, mock_session):
    # Подготовка
    mock_scheme = MagicMock(spec=InsurerScheme)
    mock_session.query.return_value.filter_by.return_value.first.return_value = mock_scheme

    # Выполнение
    result = db_client.get_insurer_scheme(1, 1)

    # Проверка
    assert result == mock_scheme
    mock_session.query.assert_called_once_with(InsurerScheme)
    mock_session.query.return_value.filter_by.assert_called_once_with(company_id=1, global_version_num=1)
    mock_session.close.assert_called_once()

def test_get_insurance_company_by_id(db_client, mock_session):
    # Подготовка
    mock_company = MagicMock(spec=CompanyInfo)
    mock_session.query.return_value.filter_by.return_value.first.return_value = mock_company

    # Выполнение
    result = db_client.get_insurance_company_by_id(1)

    # Проверка
    assert result == mock_company
    mock_session.query.assert_called_once_with(CompanyInfo)
    mock_session.query.return_value.filter_by.assert_called_once_with(id=1)
    mock_session.close.assert_called_once()

def test_get_most_popular_insurers(db_client, mock_session):
    # Подготовка
    mock_companies = [(MagicMock(spec=CompanyInfo), 10)]
    mock_query = mock_session.query.return_value
    mock_query.outerjoin.return_value = mock_query
    mock_query.group_by.return_value = mock_query
    mock_query.order_by.return_value = mock_query
    mock_query.limit.return_value = mock_query
    mock_query.all.return_value = mock_companies

    # Выполнение
    result = db_client.get_most_popular_insurers()

    # Проверка
    assert result == mock_companies
    mock_session.close.assert_called_once()

def test_get_payout(db_client, mock_session):
    # Подготовка
    mock_payout = MagicMock(spec=Payout)
    mock_session.query.return_value.filter_by.return_value.first.return_value = mock_payout
    test_date = date(2024, 1, 1)

    # Выполнение
    result = db_client.get_payout(1, 'A00', test_date)

    # Проверка
    assert result == mock_payout
    mock_session.query.assert_called_once_with(Payout)
    mock_session.query.return_value.filter_by.assert_called_once_with(user_id=1, diagnosis_code='A00', diagnosis_date=test_date)
    mock_session.close.assert_called_once()

def test_add_payout_success(db_client, mock_session):
    # Подготовка
    mock_payout = MagicMock(spec=Payout)

    # Выполнение
    result = db_client.add_payout(mock_payout)

    # Проверка
    assert result is True
    mock_session.add.assert_called_once_with(mock_payout)
    mock_session.commit.assert_called_once()
    mock_session.close.assert_called_once()

def test_add_payout_failure(db_client, mock_session):
    # Подготовка
    mock_payout = MagicMock(spec=Payout)
    mock_session.commit.side_effect = Exception('Database error')

    # Выполнение
    result = db_client.add_payout(mock_payout)

    # Проверка
    assert result is False
    mock_session.add.assert_called_once_with(mock_payout)
    mock_session.rollback.assert_called_once()
    mock_session.close.assert_called_once() 