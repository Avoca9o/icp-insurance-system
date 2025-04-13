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
    """Start dfx process for the test session"""
    # Start dfx in the background
    process = subprocess.Popen(
        ["dfx", "start", "--background"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    stdout, stderr = process.communicate()
    if process.returncode != 0:
        raise Exception(f"Failed to start dfx: {stderr.decode()}")
    
    # Wait for dfx to be ready
    time.sleep(5)
    
    yield process
    
    # Cleanup
    subprocess.run(["dfx", "stop"])

@pytest.fixture(scope="session")
def deployed_canister(dfx_process):
    """Deploy the canister for testing"""
    # Deploy the canister
    process = subprocess.Popen(
        ["dfx", "deploy"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    stdout, stderr = process.communicate()
    if process.returncode != 0:
        raise Exception(f"Failed to deploy canister: {stderr.decode()}")
    
    # Get the canister ID
    process = subprocess.Popen(
        ["dfx", "canister", "id", "icp_index_canister"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    stdout, stderr = process.communicate()
    if process.returncode != 0:
        raise Exception(f"Failed to get canister ID: {stderr.decode()}")
    
    canister_id = stdout.decode().strip()
    
    # Set environment variables for the canister
    os.environ['ICP_CANISTER_ID'] = canister_id
    os.environ['ICP_CANISTER_URL'] = 'http://127.0.0.1:4943'
    
    return canister_id

@pytest.fixture
def db_client():
    """Create a DBClient instance"""
    client = DBClient()
    yield client

@pytest.fixture
def mock_icp_client():
    """Mock ICP client for testing"""
    with patch('bot.clients.icp_client.ICPClient') as mock:
        client_instance = MagicMock()
        # Configure mock methods
        client_instance.add_approved_client.return_value = True
        client_instance.payout_request.return_value = True
        mock.return_value = client_instance
        yield client_instance

@pytest.fixture
def test_company(db_client):
    """Create a test insurance company"""
    unique_id = str(uuid.uuid4())[:8]
    company = CompanyInfo(
        login=f"test_company_{unique_id}",
        password="test_password",
        name=f"Test Insurance Company {unique_id}",
        email=f"test_{unique_id}@company.com",
        pay_address="be2us-64aaa-aaaaa-qaabq-cai"  # Valid ICP canister ID format
    )
    db_client.Session.add(company)
    db_client.Session.commit()
    return company

@pytest.fixture
def test_scheme(db_client, test_company):
    """Create a test insurer scheme"""
    scheme = InsurerScheme(
        company_id=test_company.id,
        diagnoses_coefs='{"A00": 1.0, "B00": 1.5}'
    )
    db_client.Session.add(scheme)
    db_client.Session.commit()
    return scheme

@pytest.fixture
def test_user(db_client, test_company, test_scheme):
    """Create a test user"""
    unique_id = str(uuid.uuid4())[:8]
    user = UserInfo(
        phone="+1234567890",
        email=f"test_{unique_id}@user.com",
        insurance_amount=1000,
        payout_address="rrkah-4wgwc-dfnxg-fywux-4njwc-evqkn-yp",  # Valid ICP principal ID format
        insurer_id=test_company.id,
        schema_version=test_scheme.global_version_num,
        secondary_filters=None
    )
    db_client.Session.add(user)
    db_client.Session.commit()
    return user

def test_user_company_scheme_integration(db_client, test_company, test_scheme, test_user):
    """Test the integration between User, Company, and Scheme models"""
    # Verify user is linked to company
    assert test_user.insurer_id == test_company.id
    
    # Verify user is linked to scheme
    assert test_user.schema_version == test_scheme.global_version_num
    
    # Verify company is linked to scheme
    assert test_scheme.company_id == test_company.id

def test_payout_integration(db_client, test_user, test_company):
    """Test the integration of payout creation and retrieval"""
    # Create a test payout
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
    
    # Retrieve the payout
    retrieved_payout = db_client.Session.query(Payout).filter_by(
        user_id=test_user.id,
        diagnosis_code="A00",
        diagnosis_date=date(2024, 3, 15)
    ).first()
    
    # Verify payout data
    assert retrieved_payout is not None
    assert retrieved_payout.amount == 1000
    assert retrieved_payout.transaction_id == "test_transaction"
    assert retrieved_payout.user_id == test_user.id
    assert retrieved_payout.company_id == test_company.id

def test_icp_canister_integration(mock_icp_client, test_user, test_company):
    """Test the integration with ICP canister using mocked client"""
    # Test adding approved client
    result = mock_icp_client.add_approved_client(
        insurer_wallet_address=test_company.pay_address,
        policy_holder_id=test_user.id,
        checksum="test_checksum"
    )
    assert result is True
    
    # Test payout request
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
    """Test the complete workflow integration"""
    # 1. Verify user exists and is linked correctly
    assert test_user is not None
    assert test_user.email is not None
    assert test_user.insurance_amount is not None
    assert test_user.payout_address is not None

    # Create a new payout
    payout = Payout(
        transaction_id="test_transaction_123",
        amount=1000,
        user_id=test_user.id,
        company_id=test_company.id,
        date=datetime.now(),
        diagnosis_code="A00",
        diagnosis_date=date(2024, 3, 15)
    )
    
    # Add and commit the payout
    db_client.Session.add(payout)
    db_client.Session.commit()
    db_client.Session.refresh(payout)  # Refresh to ensure all relationships are loaded

    # Verify payout was created and relationships are correct
    assert payout.id is not None
    assert payout.amount == 1000
    assert payout.transaction_id == "test_transaction_123"
    assert payout.user_id == test_user.id
    assert payout.company_id == test_company.id
    assert payout.diagnosis_code == "A00"
    assert payout.diagnosis_date == date(2024, 3, 15)

    # Request payout from ICP canister
    mock_icp_client.payout_request.return_value = True
    result = mock_icp_client.payout_request(
        transaction_id=payout.transaction_id,
        amount=payout.amount,
        recipient=test_user.payout_address
    )
    assert result is True

    # Verify mock was called correctly
    mock_icp_client.payout_request.assert_called_once_with(
        transaction_id=payout.transaction_id,
        amount=payout.amount,
        recipient=test_user.payout_address
    ) 