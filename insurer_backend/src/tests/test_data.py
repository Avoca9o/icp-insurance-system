from entities.company_info import CompanyInfo
from entities.user_info import UserInfo
from entities.insurer_scheme import InsurerScheme
from entities.payout import Payout


TEST_COMPANY_1 = CompanyInfo(
    login="test_company_1",
    password="password1",
    name="Test Company 1",
    email="company1@test.com",
    pay_address="pay_address1"
)

TEST_COMPANY_2 = CompanyInfo(
    login="test_company_2",
    password="password2",
    name="Test Company 2",
    email="company2@test.com",
    pay_address="pay_address2"
)

TEST_USER_1 = UserInfo(
    email="user1@test.com",
    insurer_id=1,
    insurance_amount=1000.0,
    schema_version=1,
    secondary_filters={
        "C34.9": 0.8,
        "I21.9": 0.6,
        "E11.9": 0.4
    },
    is_approved=False
)

TEST_USER_2 = UserInfo(
    email="user2@test.com",
    insurer_id=1,
    insurance_amount=2000.0,
    schema_version=1,
    secondary_filters={
        "C18.9": 0.7,
        "I10": 0.5,
        "E78.5": 0.3
    },
    is_approved=True
)

TEST_USER_3 = UserInfo(
    email="user3@test.com",
    insurer_id=2,
    insurance_amount=1500.0,
    schema_version=2,
    secondary_filters={
        "C50.9": 0.9,
        "I25.1": 0.7,
        "E78.2": 0.6
    },
    is_approved=False
)

TEST_SCHEME_1 = InsurerScheme(
    company_id=1,
    diagnoses_coefs=str({
        "C34.9": 1.5,
        "I21.9": 1.2,
        "E11.9": 1.1
    })
)

TEST_SCHEME_2 = InsurerScheme(
    company_id=1,
    diagnoses_coefs=str({
        "C18.9": 1.8,
        "I10": 1.3,
        "E78.5": 1.2
    })
)

TEST_SCHEME_3 = InsurerScheme(
    company_id=2,
    diagnoses_coefs=str({
        "C50.9": 1.6,
        "I25.1": 1.4,
        "E78.2": 1.3
    })
)

TEST_PAYOUT_1 = Payout(
    transaction_id="tx1",
    amount=1000,
    user_id=1,
    date="2024-01-01",
    company_id=1,
    diagnosis_code="C34.9",
    diagnosis_date="2024-01-01"
)

TEST_PAYOUT_2 = Payout(
    transaction_id="tx2",
    amount=2000,
    user_id=2,
    date="2024-01-01",
    company_id=1,
    diagnosis_code="C18.9",
    diagnosis_date="2024-01-01"
)

TEST_PAYOUT_3 = Payout(
    transaction_id="tx3",
    amount=1500,
    user_id=3,
    date="2024-01-02",
    company_id=2,
    diagnosis_code="C50.9",
    diagnosis_date="2024-01-02"
)

def init_mock_db_with_test_data(mock_db):
    mock_db.add_company(TEST_COMPANY_1)
    mock_db.add_company(TEST_COMPANY_2)

    mock_db.add_user(TEST_USER_1)
    mock_db.add_user(TEST_USER_2)
    mock_db.add_user(TEST_USER_3)

    mock_db.add_scheme(TEST_SCHEME_1)
    mock_db.add_scheme(TEST_SCHEME_2)
    mock_db.add_scheme(TEST_SCHEME_3)

    mock_db.payouts.extend([TEST_PAYOUT_1, TEST_PAYOUT_2, TEST_PAYOUT_3])
    
    return mock_db 