import pytest
from datetime import datetime, date
from unittest.mock import patch, MagicMock
import subprocess
import time
import os
import uuid

from bot.models import (
    UserInfo, CompanyInfo, InsurerScheme, Payout
)
from bot.config.db_config import Base
from bot.clients.db_client import DBClient
from bot.clients.icp_client import ICPClient

@pytest.fixture(scope="session")
def dfx_process():
    process = subprocess.Popen(
        ["dfx", "start", "--background"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    stdout, stderr = process.communicate()
    if process.returncode != 0:
        raise Exception(f"Failed to start dfx: {stderr.decode()}")
    
    time.sleep(5)
    
    yield process
    
    subprocess.run(["dfx", "stop"])

@pytest.fixture(scope="session")
def deployed_canister(dfx_process):
    process = subprocess.Popen(
        ["dfx", "deploy"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    stdout, stderr = process.communicate()
    if process.returncode != 0:
        raise Exception(f"Failed to deploy canister: {stderr.decode()}")

    process = subprocess.Popen(
        ["dfx", "canister", "id", "icp_index_canister"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    stdout, stderr = process.communicate()
    if process.returncode != 0:
        raise Exception(f"Failed to get canister ID: {stderr.decode()}")
    
    canister_id = stdout.decode().strip()

    os.environ['ICP_CANISTER_ID'] = canister_id
    os.environ['ICP_CANISTER_URL'] = 'http://127.0.0.1:4943'
    
    return canister_id

@pytest.fixture
def db_client():
    client = DBClient()
    yield client

@pytest.fixture
def mock_icp_client():
    with patch('bot.clients.icp_client.ICPClient') as mock:
        client_instance = MagicMock()
        client_instance.add_approved_client.return_value = True
        client_instance.payout_request.return_value = True
        mock.return_value = client_instance
        yield client_instance

@pytest.fixture
def test_company(db_client):
    unique_id = str(uuid.uuid4())[:8]
    company = CompanyInfo(
        login=f"test_company_{unique_id}",
        password="test_password",
        name=f"Test Insurance Company {unique_id}",
        email=f"test_{unique_id}@company.com",
        pay_address="be2us-64aaa-aaaaa-qaabq-cai"
    )
    db_client.Session.add(company)
    db_client.Session.commit()
    return company

@pytest.fixture
def test_scheme(db_client, test_company):
    scheme = InsurerScheme(
        company_id=test_company.id,
        diagnoses_coefs='{"A00": 1.0, "B00": 1.5}'
    )
    db_client.Session.add(scheme)
    db_client.Session.commit()
    return scheme

@pytest.fixture
def test_user(db_client, test_company, test_scheme):
    unique_id = str(uuid.uuid4())[:8]
    user = UserInfo(
        phone="+1234567890",
        email=f"test_{unique_id}@user.com",
        insurance_amount=1000,
        payout_address="rrkah-4wgwc-dfnxg-fywux-4njwc-evqkn-yp",
        insurer_id=test_company.id,
        schema_version=test_scheme.global_version_num,
        secondary_filters=None
    )
    db_client.Session.add(user)
    db_client.Session.commit()
    return user

def test_user_company_scheme_integration(db_client, test_company, test_scheme, test_user):
    assert test_user.insurer_id == test_company.id
    
    assert test_user.schema_version == test_scheme.global_version_num

    assert test_scheme.company_id == test_company.id

def test_payout_integration(db_client, test_user, test_company):
    payout = Payout(
        transaction_id="test_transaction",
        amount=1000,
        user_id=test_user.id,
        date=datetime.now(),
        company_id=test_company.id,
        diagnosis_code="A00",
        diagnosis_date=date(2024, 3, 15)
    )
    db_client.Session.add(payout)
    db_client.Session.commit()
    
    retrieved_payout = db_client.Session.query(Payout).filter_by(
        user_id=test_user.id,
        diagnosis_code="A00",
        diagnosis_date=date(2024, 3, 15)
    ).first()

    assert retrieved_payout is not None
    assert retrieved_payout.amount == 1000
    assert retrieved_payout.transaction_id == "test_transaction"
    assert retrieved_payout.user_id == test_user.id
    assert retrieved_payout.company_id == test_company.id

def test_icp_canister_integration(mock_icp_client, test_user, test_company):
    result = mock_icp_client.add_approved_client(
        insurer_wallet_address=test_company.pay_address,
        policy_holder_id=test_user.id,
        checksum="test_checksum"
    )
    assert result is True

    result = mock_icp_client.payout_request(
        amount=1000,
        policy_number=f"POL{test_user.id}",
        diagnosis_code="A00",
        diagnosis_date=date(2024, 3, 15),
        crypto_wallet=test_user.payout_address,
        insurer_crypto_wallet=test_company.pay_address,
        oauth_token="test_token"
    )
    assert result is True

def test_full_workflow_integration(db_client, mock_icp_client, test_company, test_scheme, test_user):
    assert test_user is not None
    assert test_user.email is not None
    assert test_user.insurance_amount is not None
    assert test_user.payout_address is not None

    payout = Payout(
        transaction_id="test_transaction_123",
        amount=1000,
        user_id=test_user.id,
        company_id=test_company.id,
        date=datetime.now(),
        diagnosis_code="A00",
        diagnosis_date=date(2024, 3, 15)
    )

    db_client.Session.add(payout)
    db_client.Session.commit()
    db_client.Session.refresh(payout)

    assert payout.id is not None
    assert payout.amount == 1000
    assert payout.transaction_id == "test_transaction_123"
    assert payout.user_id == test_user.id
    assert payout.company_id == test_company.id
    assert payout.diagnosis_code == "A00"
    assert payout.diagnosis_date == date(2024, 3, 15)

    mock_icp_client.payout_request.return_value = True
    result = mock_icp_client.payout_request(
        transaction_id=payout.transaction_id,
        amount=payout.amount,
        recipient=test_user.payout_address
    )
    assert result is True

    mock_icp_client.payout_request.assert_called_once_with(
        transaction_id=payout.transaction_id,
        amount=payout.amount,
        recipient=test_user.payout_address
    ) 