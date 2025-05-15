import pytest
from fastapi.testclient import TestClient
from fastapi import FastAPI
from handlers.ping import router as ping_router, handle_ping
from handlers.v1_register import router as register_router, RegisterRequest, handle_v1_register
from handlers.v1_authorize import router as auth_router, AuthorizationRequest, handle_v1_authorize
from handlers.v1_balance import handle_v1_balance_request
from handlers.v1_schemas import handle_v1_schemas
from handlers.v1_schema import handle_v1_schema
from handlers.v1_add_schema import handle_v1_add_scheme, AddSchemaRequest, handle_v1_add_scheme_csv
from handlers.v1_add_user import handle_v1_add_user, AddUserRequest
from handlers.v1_check_sum import handle_v1_check_sum
from handlers.v1_icp_address import handle_v1_icp_address_get
from handlers.v1_operations import handle_v1_operations, GetOperationsRequest
from handlers.v1_update_user import handle_v1_update_user, UpdateUserRequest
from handlers.v1_user import handle_v1_user_get, handle_v1_user_delete
from handlers.v1_users import handle_v1_users_get
from handlers.v1_withdraw import handle_v1_withdraw_post
from tests.mock_db_client import MockDBClient
from tests.mock_icp_client import MockICPClient
from tests.test_data import init_mock_db_with_test_data, TEST_COMPANY_1, TEST_SCHEME_1
from unittest.mock import patch, MagicMock, ANY
from fastapi.responses import JSONResponse, Response
from utils.jwt import create_jwt_token

test_app = FastAPI()
test_app.include_router(ping_router)
test_app.include_router(register_router)
test_app.include_router(auth_router)
client = TestClient(test_app)


def test_handle_ping():
    response = handle_ping()
    assert isinstance(response, JSONResponse)
    assert response.status_code == 200
    assert response.body == b'{"message":"Hello world"}'


def test_register_request_validity():
    valid_request = RegisterRequest(
        login="test",
        password="test",
        name="Test Company",
        email="test@test.com",
        pay_address="test_address"
    )
    valid_request.check_validity()


def test_register_request_invalid_login():
    with pytest.raises(ValueError, match="login should not be empty"):
        RegisterRequest(
            login="",
            password="test",
            name="Test Company",
            email="test@test.com",
            pay_address="test_address"
        ).check_validity()


def test_register_request_invalid_name():
    with pytest.raises(ValueError, match="name should not be empty"):
        RegisterRequest(
            login="test",
            password="test",
            name="",
            email="test@test.com",
            pay_address="test_address"
        ).check_validity()


def test_register_request_invalid_email():
    with pytest.raises(ValueError, match="email should not be empty"):
        RegisterRequest(
            login="test",
            password="test",
            name="Test Company",
            email="",
            pay_address="test_address"
        ).check_validity()


def test_register_request_invalid_password():
    with pytest.raises(ValueError, match="password should not be empty"):
        RegisterRequest(
            login="test",
            password="",
            name="Test Company",
            email="test@test.com",
            pay_address="test_address"
        ).check_validity()


def test_register_request_invalid_pay_address():
    with pytest.raises(ValueError, match="pay_address should not be empty"):
        RegisterRequest(
            login="test",
            password="test",
            name="Test Company",
            email="test@test.com",
            pay_address=""
        ).check_validity()


def test_register_request_as_company_info():
    request = RegisterRequest(
        login="test",
        password="test",
        name="Test Company",
        email="test@test.com",
        pay_address="test_address"
    )
    company_info = request.as_company_info()
    assert company_info.login == "test"
    assert company_info.password == "test"
    assert company_info.name == "Test Company"
    assert company_info.email == "test@test.com"
    assert company_info.pay_address == "test_address"


def test_handle_v1_register_success():
    mock_db = MockDBClient()
    mock_icp = MockICPClient()

    with patch('handlers.v1_register.db', mock_db), \
         patch('handlers.v1_register.icp', mock_icp):
        request = RegisterRequest(
            login="new_company",
            password="password",
            name="New Company",
            email="new@company.com",
            pay_address="new_address"
        )
        response = handle_v1_register(request)

        assert isinstance(response, JSONResponse)
        assert response.status_code == 200
        assert response.body == b'null'
        assert "new_company" in [c.login for c in mock_db.companies.values()]
        assert "new_address" in mock_icp.registered_companies


def test_handle_v1_register_duplicate_login():
    mock_db = MockDBClient()
    mock_icp = MockICPClient()
    init_mock_db_with_test_data(mock_db)

    with patch('handlers.v1_register.db', mock_db), \
         patch('handlers.v1_register.icp', mock_icp):
        request = RegisterRequest(
            login=TEST_COMPANY_1.login,
            password="password",
            name="New Company",
            email="new@company.com",
            pay_address="new_address"
        )
        response = handle_v1_register(request)

        assert isinstance(response, JSONResponse)
        assert response.status_code == 400
        assert b"already exists" in response.body


def test_handle_v1_register_validation_error():
    mock_db = MockDBClient()
    mock_icp = MockICPClient()

    with patch('handlers.v1_register.db', mock_db), \
         patch('handlers.v1_register.icp', mock_icp):
        request = RegisterRequest(
            login="",
            password="password",
            name="New Company",
            email="new@company.com",
            pay_address="new_address"
        )
        response = handle_v1_register(request)

        assert isinstance(response, JSONResponse)
        assert response.status_code == 400
        assert b"login should not be empty" in response.body


def test_authorization_request_validity():
    valid_request = AuthorizationRequest(login="test", password="test")
    valid_request.check_validity()


def test_authorization_request_invalid_login():
    with pytest.raises(ValueError, match="login should not be empty"):
        AuthorizationRequest(login="", password="test").check_validity()


def test_authorization_request_invalid_password():
    with pytest.raises(ValueError, match="password should not be empty"):
        AuthorizationRequest(login="test", password="").check_validity()


def test_handle_v1_authorize_success():
    mock_db = MockDBClient()
    init_mock_db_with_test_data(mock_db)

    with patch('handlers.v1_authorize.db', mock_db):
        request = AuthorizationRequest(
            login=TEST_COMPANY_1.login,
            password=TEST_COMPANY_1.password
        )
        response = handle_v1_authorize(request)

        assert isinstance(response, JSONResponse)
        assert response.status_code == 200
        assert b"access_token" in response.body


def test_handle_v1_authorize_invalid_input():
    mock_db = MockDBClient()

    with patch('handlers.v1_authorize.db', mock_db):
        request = AuthorizationRequest(login="", password="test")
        response = handle_v1_authorize(request)

        assert isinstance(response, JSONResponse)
        assert response.status_code == 400
        assert b"login should not be empty" in response.body


def test_handle_v1_authorize_wrong_credentials():
    mock_db = MockDBClient()
    init_mock_db_with_test_data(mock_db)

    with patch('handlers.v1_authorize.db', mock_db):
        request = AuthorizationRequest(
            login=TEST_COMPANY_1.login,
            password="wrong_password"
        )
        response = handle_v1_authorize(request)

        assert isinstance(response, JSONResponse)
        assert response.status_code == 400
        assert b"Invalid password" in response.body


def test_handle_v1_authorize_server_error():
    mock_db = MockDBClient()
    init_mock_db_with_test_data(mock_db)

    def raise_error(*args, **kwargs):
        raise Exception("Database error")

    mock_db.authorize_company = raise_error

    with patch('handlers.v1_authorize.db', mock_db):
        request = AuthorizationRequest(
            login=TEST_COMPANY_1.login,
            password=TEST_COMPANY_1.password
        )
        response = handle_v1_authorize(request)

        assert isinstance(response, JSONResponse)
        assert response.status_code == 500
        assert b"Database error" in response.body


def test_handle_v1_balance_success():
    mock_db = MockDBClient()
    mock_icp = MockICPClient()
    init_mock_db_with_test_data(mock_db)

    token = create_jwt_token(data={"id": 1})

    mock_icp.register_company(TEST_COMPANY_1.pay_address)
    mock_icp.set_balance(TEST_COMPANY_1.pay_address, 100.0)

    with patch('handlers.v1_balance.db', mock_db), \
         patch('handlers.v1_balance.icp', mock_icp):
        response = handle_v1_balance_request(token)

        assert isinstance(response, JSONResponse)
        assert response.status_code == 200
        assert b"Your balance is" in response.body
        assert b"dirhum" in response.body


def test_handle_v1_balance_company_not_found():
    mock_db = MockDBClient()
    mock_icp = MockICPClient()

    token = create_jwt_token(data={"id": 999})

    with patch('handlers.v1_balance.db', mock_db), \
         patch('handlers.v1_balance.icp', mock_icp):
        response = handle_v1_balance_request(token)

        assert isinstance(response, JSONResponse)
        assert response.status_code == 400
        assert b"Company does not exist" in response.body


def test_handle_v1_balance_invalid_token():
    mock_db = MockDBClient()
    mock_icp = MockICPClient()

    with patch('handlers.v1_balance.db', mock_db), \
         patch('handlers.v1_balance.icp', mock_icp):
        response = handle_v1_balance_request("invalid_token")

        assert isinstance(response, JSONResponse)
        assert response.status_code == 500
        assert b"message" in response.body


def test_handle_v1_balance_server_error():
    mock_db = MockDBClient()
    mock_icp = MockICPClient()
    init_mock_db_with_test_data(mock_db)

    token = create_jwt_token(data={"id": 1})

    def raise_error(*args, **kwargs):
        raise Exception("Database error")

    mock_db.get_company = raise_error

    with patch('handlers.v1_balance.db', mock_db), \
         patch('handlers.v1_balance.icp', mock_icp):
        response = handle_v1_balance_request(token)

        assert isinstance(response, JSONResponse)
        assert response.status_code == 500
        assert b"Database error" in response.body


def test_handle_v1_schemas_success():
    mock_db = MockDBClient()
    init_mock_db_with_test_data(mock_db)

    token = create_jwt_token(data={"id": 1})

    with patch('handlers.v1_schemas.db', mock_db):
        response = handle_v1_schemas(token)

        assert isinstance(response, JSONResponse)
        assert response.status_code == 200
        assert len(response.body) > 0


def test_handle_v1_schemas_company_not_found():
    mock_db = MockDBClient()

    token = create_jwt_token(data={"id": 999})

    with patch('handlers.v1_schemas.db', mock_db):
        response = handle_v1_schemas(token)

        assert isinstance(response, JSONResponse)
        assert response.status_code == 400
        assert b"Company does not exist" in response.body


def test_handle_v1_schemas_invalid_token():
    mock_db = MockDBClient()

    with patch('handlers.v1_schemas.db', mock_db):
        response = handle_v1_schemas("invalid_token")

        assert isinstance(response, JSONResponse)
        assert response.status_code == 500
        assert b"message" in response.body


def test_handle_v1_schemas_server_error():
    mock_db = MockDBClient()
    init_mock_db_with_test_data(mock_db)

    token = create_jwt_token(data={"id": 1})

    def raise_error(*args, **kwargs):
        raise Exception("Database error")

    mock_db.get_schemas = raise_error

    with patch('handlers.v1_schemas.db', mock_db):
        response = handle_v1_schemas(token)

        assert isinstance(response, JSONResponse)
        assert response.status_code == 500
        assert b"Database error" in response.body


def test_handle_v1_schema_invalid_json():
    mock_db = MockDBClient()
    init_mock_db_with_test_data(mock_db)

    token = create_jwt_token(data={"id": 1})

    def get_invalid_schema(global_version_id):
        from entities.insurer_scheme import InsurerScheme
        return InsurerScheme(
            id=1,
            company_id=1,
            diagnoses_coefs="{invalid json",
            global_version_id=1
        )

    mock_db.get_schema = get_invalid_schema

    with patch('handlers.v1_schema.db', mock_db):
        response = handle_v1_schema(global_version_id=1, token=token)

        assert isinstance(response, JSONResponse)
        assert response.status_code == 500
        assert b"message" in response.body


def test_handle_v1_schema_value_error():
    mock_db = MockDBClient()
    init_mock_db_with_test_data(mock_db)

    token = create_jwt_token(data={"id": 1})

    def raise_value_error(*args, **kwargs):
        raise ValueError("Custom value error")

    mock_db.get_schema = raise_value_error

    with patch('handlers.v1_schema.db', mock_db):
        response = handle_v1_schema(global_version_id=1, token=token)

        assert isinstance(response, JSONResponse)
        assert response.status_code == 400
        assert b"Custom value error" in response.body


def test_handle_v1_schema_single_quotes():
    mock_db = MockDBClient()
    init_mock_db_with_test_data(mock_db)

    token = create_jwt_token(data={"id": 1})

    def get_schema_with_valid_json(global_version_id):
        from entities.insurer_scheme import InsurerScheme
        return InsurerScheme(
            company_id=1,
            diagnoses_coefs='{"key": "value"}'
        )

    mock_db.get_schema = get_schema_with_valid_json

    with patch('handlers.v1_schema.db', mock_db):
        response = handle_v1_schema(global_version_id=1, token=token)

        print(f"Response status code: {response.status_code}")
        print(f"Response body: {response.body}")

        assert isinstance(response, JSONResponse)
        assert response.status_code == 200
        assert b'{"scheme":"{\\"key\\": \\"value\\"}"}' == response.body


def test_handle_v1_add_scheme_success():
    mock_db = MockDBClient()
    init_mock_db_with_test_data(mock_db)

    token = create_jwt_token(data={"id": 1})

    request = AddSchemaRequest(diagnoses_coefs='{"key": "value"}')

    with patch('handlers.v1_add_schema.db', mock_db):
        response = handle_v1_add_scheme(request, token)

        assert isinstance(response, JSONResponse)
        assert response.status_code == 200
        assert response.body == b'null'


def test_handle_v1_add_scheme_invalid_token():
    mock_db = MockDBClient()

    request = AddSchemaRequest(diagnoses_coefs='{"key": "value"}')

    with patch('handlers.v1_add_schema.db', mock_db):
        response = handle_v1_add_scheme(request, "invalid_token")

        assert isinstance(response, JSONResponse)
        assert response.status_code == 500
        assert b"message" in response.body


def test_handle_v1_add_scheme_server_error():
    mock_db = MockDBClient()
    init_mock_db_with_test_data(mock_db)

    token = create_jwt_token(data={"id": 1})

    request = AddSchemaRequest(diagnoses_coefs='{"key": "value"}')

    def raise_error(*args, **kwargs):
        raise Exception("Database error")

    mock_db.add_scheme = raise_error

    with patch('handlers.v1_add_schema.db', mock_db):
        response = handle_v1_add_scheme(request, token)

        assert isinstance(response, JSONResponse)
        assert response.status_code == 500
        assert b"Database error" in response.body


def test_handle_v1_add_scheme_csv_success():
    mock_db = MockDBClient()
    init_mock_db_with_test_data(mock_db)

    token = create_jwt_token(data={"id": 1})

    mock_file = MagicMock()
    mock_file.content_type = 'text/csv'
    mock_file.file = MagicMock()
    mock_file.file.seek = MagicMock()
    mock_file.file.read = MagicMock(return_value=b'Code,Coefficient\nC34.9,1.0')

    with patch('handlers.v1_add_schema.db', mock_db), \
         patch('handlers.v1_add_schema.pd.read_csv') as mock_read_csv:
        mock_df = MagicMock()
        mock_df.Coefficient.values = [1.0]
        mock_df.Code = ['C34.9']
        mock_read_csv.return_value = mock_df

        response = handle_v1_add_scheme_csv(mock_file, token)

        assert isinstance(response, JSONResponse)
        assert response.status_code == 200
        assert response.body == b'null'
        mock_file.file.seek.assert_called_once_with(0)
        mock_read_csv.assert_called_once_with(mock_file.file)


def test_handle_v1_add_scheme_csv_invalid_format():
    mock_db = MockDBClient()
    init_mock_db_with_test_data(mock_db)

    token = create_jwt_token(data={"id": 1})

    mock_file = MagicMock()
    mock_file.content_type = 'text/plain'

    with patch('handlers.v1_add_schema.db', mock_db):
        response = handle_v1_add_scheme_csv(mock_file, token)

        assert isinstance(response, JSONResponse)
        assert response.status_code == 400
        assert b"Invalid file format. CSV required" in response.body


def test_handle_v1_add_scheme_csv_invalid_token():
    mock_db = MockDBClient()

    mock_file = MagicMock()
    mock_file.content_type = 'text/csv'

    with patch('handlers.v1_add_schema.db', mock_db):
        response = handle_v1_add_scheme_csv(mock_file, "invalid_token")

        assert isinstance(response, JSONResponse)
        assert response.status_code == 500
        assert b"message" in response.body


def test_handle_v1_add_scheme_csv_server_error():
    mock_db = MockDBClient()
    init_mock_db_with_test_data(mock_db)

    token = create_jwt_token(data={"id": 1})

    mock_file = MagicMock()
    mock_file.content_type = 'text/csv'
    mock_file.file = MagicMock()
    mock_file.file.seek = MagicMock()
    mock_file.file.read = MagicMock(return_value=b'Code,Coefficient\nC34.9,1.0')

    def raise_error(*args, **kwargs):
        raise Exception("Database error")

    mock_db.add_scheme = raise_error

    with patch('handlers.v1_add_schema.db', mock_db), \
         patch('handlers.v1_add_schema.pd.read_csv') as mock_read_csv:
        mock_df = MagicMock()
        mock_df.Coefficient.values = [1.0]
        mock_df.Code = ['C34.9']
        mock_read_csv.return_value = mock_df

        response = handle_v1_add_scheme_csv(mock_file, token)

        assert isinstance(response, JSONResponse)
        assert response.status_code == 500
        assert b"Database error" in response.body


def test_handle_v1_add_user_success():
    mock_db = MockDBClient()
    init_mock_db_with_test_data(mock_db)

    token = create_jwt_token(data={"id": 1})

    request = AddUserRequest(
        email="test@example.com",
        insurance_amount=1000,
        schema_version=1,
        secondary_filters={"C34.9": 1.0}
    )

    with patch('handlers.v1_add_user.db', mock_db):
        response = handle_v1_add_user(request, token)

        assert isinstance(response, JSONResponse)
        assert response.status_code == 200
        assert response.body == b'null'


def test_handle_v1_add_user_invalid_email():
    mock_db = MockDBClient()
    init_mock_db_with_test_data(mock_db)

    token = create_jwt_token(data={"id": 1})

    request = AddUserRequest(
        email="",
        insurance_amount=1000,
        schema_version=1,
        secondary_filters={"C34.9": 1.0}
    )

    with patch('handlers.v1_add_user.db', mock_db):
        response = handle_v1_add_user(request, token)

        assert isinstance(response, JSONResponse)
        assert response.status_code == 400
        assert b"Phone number name cannot be empty" in response.body


def test_handle_v1_add_user_invalid_token():
    mock_db = MockDBClient()

    request = AddUserRequest(
        email="test@example.com",
        insurance_amount=1000,
        schema_version=1,
        secondary_filters={"C34.9": 1.0}
    )

    with patch('handlers.v1_add_user.db', mock_db):
        response = handle_v1_add_user(request, "invalid_token")

        assert isinstance(response, JSONResponse)
        assert response.status_code == 500
        assert b"message" in response.body


def test_handle_v1_add_user_server_error():
    mock_db = MockDBClient()
    init_mock_db_with_test_data(mock_db)

    token = create_jwt_token(data={"id": 1})

    request = AddUserRequest(
        email="test@example.com",
        insurance_amount=1000,
        schema_version=1,
        secondary_filters={"C34.9": 1.0}
    )

    def raise_error(*args, **kwargs):
        raise Exception("Database error")

    mock_db.add_user = raise_error

    with patch('handlers.v1_add_user.db', mock_db):
        response = handle_v1_add_user(request, token)

        assert isinstance(response, JSONResponse)
        assert response.status_code == 500
        assert b"Database error" in response.body


def test_handle_v1_check_sum_success():
    mock_db = MockDBClient()
    mock_icp = MockICPClient()
    init_mock_db_with_test_data(mock_db)

    token = create_jwt_token(data={"id": 1})

    mock_user = {
        "is_approved": True,
        "scheme_version": 1,
        "secondary_filters": '{"C34.9": 1.0}',
        "telegram_id": 123
    }
    mock_db.get_user = MagicMock(return_value=mock_user)

    mock_schema = MagicMock()
    mock_schema.diagnoses_coefs = '{"C34.9": 1.0}'
    mock_db.get_schema = MagicMock(return_value=mock_schema)

    mock_icp.is_checksum_valid = MagicMock(return_value=True)

    with patch('handlers.v1_check_sum.db', mock_db), \
         patch('handlers.v1_check_sum.icp', mock_icp):
        response = handle_v1_check_sum("test@example.com", token)

        assert isinstance(response, JSONResponse)
        assert response.status_code == 200
        assert b"is_valid" in response.body
        assert b"true" in response.body.lower()
        mock_db.get_user.assert_called_once_with("test@example.com", 1)
        mock_db.get_schema.assert_called_once_with(1)
        mock_icp.is_checksum_valid.assert_called_once_with(1, 123, ANY)


def test_handle_v1_check_sum_not_approved():
    mock_db = MockDBClient()
    mock_icp = MockICPClient()
    init_mock_db_with_test_data(mock_db)

    token = create_jwt_token(data={"id": 1})

    mock_user = {
        "is_approved": False,
        "scheme_version": 1,
        "secondary_filters": '{"C34.9": 1.0}',
        "telegram_id": 123
    }
    mock_db.get_user = MagicMock(return_value=mock_user)

    with patch('handlers.v1_check_sum.db', mock_db), \
         patch('handlers.v1_check_sum.icp', mock_icp):
        response = handle_v1_check_sum("test@example.com", token)

        assert isinstance(response, JSONResponse)
        assert response.status_code == 400
        assert b"can't validate check sum while user's contract is not approved" in response.body
        mock_db.get_user.assert_called_once_with("test@example.com", 1)


def test_handle_v1_check_sum_invalid_token():
    mock_db = MockDBClient()
    mock_icp = MockICPClient()

    with patch('handlers.v1_check_sum.db', mock_db), \
         patch('handlers.v1_check_sum.icp', mock_icp):
        response = handle_v1_check_sum("test@example.com", "invalid_token")

        assert isinstance(response, JSONResponse)
        assert response.status_code == 500
        assert b"message" in response.body


def test_handle_v1_check_sum_server_error():
    mock_db = MockDBClient()
    mock_icp = MockICPClient()
    init_mock_db_with_test_data(mock_db)

    token = create_jwt_token(data={"id": 1})

    def raise_error(*args, **kwargs):
        raise Exception("Database error")

    mock_db.get_user = raise_error

    with patch('handlers.v1_check_sum.db', mock_db), \
         patch('handlers.v1_check_sum.icp', mock_icp):
        response = handle_v1_check_sum("test@example.com", token)

        assert isinstance(response, JSONResponse)
        assert response.status_code == 500
        assert b"Database error" in response.body


def test_handle_v1_icp_address_get_success():
    token = create_jwt_token(data={"id": 1})

    mock_canister_id = "test_canister_id"

    with patch('handlers.v1_icp_address.CANISTER_ID', mock_canister_id):
        response = handle_v1_icp_address_get(token)

        assert isinstance(response, JSONResponse)
        assert response.status_code == 200
        assert b"icp_address" in response.body
        assert mock_canister_id.encode() in response.body


def test_handle_v1_icp_address_get_invalid_token():
    mock_canister_id = "test_canister_id"

    with patch('handlers.v1_icp_address.CANISTER_ID', mock_canister_id):
        response = handle_v1_icp_address_get("invalid_token")

        assert isinstance(response, JSONResponse)
        assert response.status_code == 500
        assert b"message" in response.body


def test_get_operations_request_validity():
    valid_request = GetOperationsRequest(company_id=1, date="2024-03-20")
    valid_request.check_validity()

    with pytest.raises(ValueError, match="Date cannot be empty"):
        invalid_request = GetOperationsRequest(company_id=1, date="")
        invalid_request.check_validity()


def test_handle_v1_operations_success():
    mock_db = MockDBClient()
    init_mock_db_with_test_data(mock_db)

    token = create_jwt_token(data={"id": 1})

    mock_operations = [
        {"user": "user1", "amount": 100, "date": "2024-03-20 10:00:00", "diagnoses": "C34.9"},
        {"user": "user2", "amount": 200, "date": "2024-03-20 11:00:00", "diagnoses": "C34.8"}
    ]
    mock_db.get_payouts_by_company_and_date = MagicMock(return_value=mock_operations)

    with patch('handlers.v1_operations.db', mock_db):
        response = handle_v1_operations("2024-03-20", token)

        assert isinstance(response, Response)
        assert response.media_type == "text/csv"
        assert "Content-Disposition" in response.headers
        assert "attachment; filename=data.csv" in response.headers["Content-Disposition"]
        
        content = response.body.decode('utf-8')
        assert "User,Amount,Date,Diagnoses" in content
        assert "user1,100,2024-03-20 ,C34.9" in content
        assert "user2,200,2024-03-20 ,C34.8" in content

        mock_db.get_payouts_by_company_and_date.assert_called_once_with(1, "2024-03-20")


def test_handle_v1_operations_empty_date():
    mock_db = MockDBClient()
    init_mock_db_with_test_data(mock_db)

    token = create_jwt_token(data={"id": 1})

    def raise_error(*args, **kwargs):
        raise ValueError("Date cannot be empty")

    mock_db.get_payouts_by_company_and_date = raise_error

    with patch('handlers.v1_operations.db', mock_db):
        response = handle_v1_operations("", token)

        assert isinstance(response, JSONResponse)
        assert response.status_code == 400
        assert b"Date cannot be empty" in response.body


def test_handle_v1_operations_invalid_token():
    mock_db = MockDBClient()

    with patch('handlers.v1_operations.db', mock_db):
        response = handle_v1_operations("2024-03-20", "invalid_token")

        assert isinstance(response, JSONResponse)
        assert response.status_code == 500
        assert b"message" in response.body


def test_handle_v1_operations_server_error():
    mock_db = MockDBClient()
    init_mock_db_with_test_data(mock_db)

    token = create_jwt_token(data={"id": 1})

    def raise_error(*args, **kwargs):
        raise Exception("Database error")

    mock_db.get_payouts_by_company_and_date = raise_error

    with patch('handlers.v1_operations.db', mock_db):
        response = handle_v1_operations("2024-03-20", token)

        assert isinstance(response, JSONResponse)
        assert response.status_code == 500
        assert b"Database error" in response.body


def test_update_user_request_validity():
    valid_request = UpdateUserRequest(
        email="test@example.com",
        insurance_amount=1000,
        insurer_schema=1,
        secondary_filters={"C34.9": 1.0}
    )
    valid_request.check_validity()

    with pytest.raises(ValueError, match="Phone number name cannot be empty in update user request"):
        invalid_request = UpdateUserRequest(email="")
        invalid_request.check_validity()


def test_handle_v1_update_user_success():
    mock_db = MockDBClient()
    init_mock_db_with_test_data(mock_db)

    token = create_jwt_token(data={"id": 1})

    request = UpdateUserRequest(
        email="user1@test.com",
        insurance_amount=2000,
        insurer_schema=2,
        secondary_filters={"C34.9": 1.5}
    )

    with patch('handlers.v1_update_user.db', mock_db):
        response = handle_v1_update_user(request, token)

        assert isinstance(response, JSONResponse)
        assert response.status_code == 200
        assert response.body == b'null'


def test_handle_v1_update_user_invalid_email():
    mock_db = MockDBClient()
    init_mock_db_with_test_data(mock_db)

    token = create_jwt_token(data={"id": 1})

    request = UpdateUserRequest(email="")

    with patch('handlers.v1_update_user.db', mock_db):
        response = handle_v1_update_user(request, token)

        assert isinstance(response, JSONResponse)
        assert response.status_code == 400
        assert b"Phone number name cannot be empty" in response.body


def test_handle_v1_update_user_not_found():
    mock_db = MockDBClient()
    init_mock_db_with_test_data(mock_db)

    token = create_jwt_token(data={"id": 1})

    request = UpdateUserRequest(
        email="nonexistent@example.com",
        insurance_amount=1000,
        insurer_schema=1,
        secondary_filters={"C34.9": 1.0}
    )

    with patch('handlers.v1_update_user.db', mock_db):
        response = handle_v1_update_user(request, token)

        assert isinstance(response, JSONResponse)
        assert response.status_code == 400
        assert b"user with email" in response.body


def test_handle_v1_update_user_wrong_company():
    mock_db = MockDBClient()
    init_mock_db_with_test_data(mock_db)

    token = create_jwt_token(data={"id": 2})

    request = UpdateUserRequest(
        email="user1@test.com",
        insurance_amount=1000,
        insurer_schema=1,
        secondary_filters={"C34.9": 1.0}
    )

    with patch('handlers.v1_update_user.db', mock_db):
        response = handle_v1_update_user(request, token)

        assert isinstance(response, JSONResponse)
        assert response.status_code == 400
        assert b"is not in company's users list" in response.body


def test_handle_v1_update_user_already_approved():
    mock_db = MockDBClient()
    init_mock_db_with_test_data(mock_db)

    token = create_jwt_token(data={"id": 1})

    request = UpdateUserRequest(
        email="user2@test.com",
        insurance_amount=1000,
        insurer_schema=1,
        secondary_filters={"C34.9": 1.0}
    )

    with patch('handlers.v1_update_user.db', mock_db):
        response = handle_v1_update_user(request, token)

        assert isinstance(response, JSONResponse)
        assert response.status_code == 400
        assert b"has already approved his info" in response.body


def test_handle_v1_update_user_invalid_token():
    mock_db = MockDBClient()

    request = UpdateUserRequest(email="user1@test.com")

    with patch('handlers.v1_update_user.db', mock_db):
        response = handle_v1_update_user(request, "invalid_token")

        assert isinstance(response, JSONResponse)
        assert response.status_code == 500
        assert b"message" in response.body


def test_handle_v1_update_user_server_error():
    mock_db = MockDBClient()
    init_mock_db_with_test_data(mock_db)

    token = create_jwt_token(data={"id": 1})

    request = UpdateUserRequest(
        email="user1@test.com",
        insurance_amount=1000,
        insurer_schema=1,
        secondary_filters={"C34.9": 1.0}
    )

    def raise_error(*args, **kwargs):
        raise Exception("Database error")

    mock_db.update_user = raise_error

    with patch('handlers.v1_update_user.db', mock_db):
        response = handle_v1_update_user(request, token)

        assert isinstance(response, JSONResponse)
        assert response.status_code == 500
        assert b"Database error" in response.body


def test_handle_v1_user_get_success():
    mock_db = MockDBClient()
    init_mock_db_with_test_data(mock_db)

    token = create_jwt_token(data={"id": 1})

    mock_user = {
        "email": "user1@test.com",
        "scheme_version": 1,
        "insurance_amount": 1000,
        "secondary_filters": '{"C34.9": 1.0}',
        "telegram_id": 123,
        "is_approved": False
    }
    mock_db.get_user = MagicMock(return_value=mock_user)

    with patch('handlers.v1_user.db', mock_db):
        response = handle_v1_user_get("user1@test.com", token)

        assert isinstance(response, JSONResponse)
        assert response.status_code == 200
        assert b"user" in response.body


def test_handle_v1_user_get_not_found():
    mock_db = MockDBClient()
    init_mock_db_with_test_data(mock_db)

    token = create_jwt_token(data={"id": 1})

    def raise_error(*args, **kwargs):
        raise ValueError("user with email nonexistent@example.com not exists")

    mock_db.get_user = raise_error

    with patch('handlers.v1_user.db', mock_db):
        response = handle_v1_user_get("nonexistent@example.com", token)

        assert isinstance(response, JSONResponse)
        assert response.status_code == 400
        assert b"user with email" in response.body
        assert b"not exists" in response.body


def test_handle_v1_user_get_invalid_token():
    mock_db = MockDBClient()

    with patch('handlers.v1_user.db', mock_db):
        response = handle_v1_user_get("user1@test.com", "invalid_token")

        assert isinstance(response, JSONResponse)
        assert response.status_code == 500
        assert b"message" in response.body


def test_handle_v1_user_get_server_error():
    mock_db = MockDBClient()
    init_mock_db_with_test_data(mock_db)

    token = create_jwt_token(data={"id": 1})

    def raise_error(*args, **kwargs):
        raise Exception("Database error")

    mock_db.get_user = raise_error

    with patch('handlers.v1_user.db', mock_db):
        response = handle_v1_user_get("user1@test.com", token)

        assert isinstance(response, JSONResponse)
        assert response.status_code == 500
        assert b"Database error" in response.body


def test_handle_v1_user_delete_success():
    mock_db = MockDBClient()
    init_mock_db_with_test_data(mock_db)

    token = create_jwt_token(data={"id": 1})

    with patch('handlers.v1_user.db', mock_db):
        response = handle_v1_user_delete("user1@test.com", token)

        assert isinstance(response, JSONResponse)
        assert response.status_code == 200
        assert response.body == b'null'


def test_handle_v1_user_delete_not_found():
    mock_db = MockDBClient()
    init_mock_db_with_test_data(mock_db)

    token = create_jwt_token(data={"id": 1})

    with patch('handlers.v1_user.db', mock_db):
        response = handle_v1_user_delete("nonexistent@example.com", token)

        assert isinstance(response, JSONResponse)
        assert response.status_code == 400
        assert b"user with email" in response.body
        assert b"not exists" in response.body


def test_handle_v1_user_delete_invalid_token():
    mock_db = MockDBClient()

    with patch('handlers.v1_user.db', mock_db):
        response = handle_v1_user_delete("user1@test.com", "invalid_token")

        assert isinstance(response, JSONResponse)
        assert response.status_code == 500
        assert b"message" in response.body


def test_handle_v1_user_delete_server_error():
    mock_db = MockDBClient()
    init_mock_db_with_test_data(mock_db)

    token = create_jwt_token(data={"id": 1})

    def raise_error(*args, **kwargs):
        raise Exception("Database error")

    mock_db.delete_user = raise_error

    with patch('handlers.v1_user.db', mock_db):
        response = handle_v1_user_delete("user1@test.com", token)

        assert isinstance(response, JSONResponse)
        assert response.status_code == 500
        assert b"Database error" in response.body


def test_handle_v1_users_get_success():
    mock_db = MockDBClient()
    init_mock_db_with_test_data(mock_db)

    token = create_jwt_token(data={"id": 1})

    mock_users = {
        "users": [
            {"email": "user1@test.com"},
            {"email": "user2@test.com"}
        ]
    }
    mock_db.get_users = MagicMock(return_value=mock_users)

    with patch('handlers.v1_users.db', mock_db):
        response = handle_v1_users_get(token)

        assert isinstance(response, JSONResponse)
        assert response.status_code == 200
        assert b"users" in response.body


def test_handle_v1_users_get_invalid_token():
    mock_db = MockDBClient()

    with patch('handlers.v1_users.db', mock_db):
        response = handle_v1_users_get("invalid_token")

        assert isinstance(response, JSONResponse)
        assert response.status_code == 500
        assert b"message" in response.body


def test_handle_v1_users_get_server_error():
    mock_db = MockDBClient()
    init_mock_db_with_test_data(mock_db)

    token = create_jwt_token(data={"id": 1})

    def raise_error(*args, **kwargs):
        raise Exception("Database error")

    mock_db.get_users = raise_error

    with patch('handlers.v1_users.db', mock_db):
        response = handle_v1_users_get(token)

        assert isinstance(response, JSONResponse)
        assert response.status_code == 500
        assert b"Database error" in response.body


def test_handle_v1_withdraw_post_success():
    mock_db = MockDBClient()
    mock_icp = MockICPClient()
    init_mock_db_with_test_data(mock_db)

    token = create_jwt_token(data={"id": 1})

    mock_db.get_users = MagicMock(return_value={"users": []})

    mock_company = MagicMock()
    mock_company.pay_address = "test_address"
    mock_db.get_company = MagicMock(return_value=mock_company)

    mock_icp.withdraw = MagicMock()

    with patch('handlers.v1_withdraw.db', mock_db), \
         patch('handlers.v1_withdraw.icp', mock_icp):
        response = handle_v1_withdraw_post(token)

        assert isinstance(response, JSONResponse)
        assert response.status_code == 200
        assert response.body == b'null'
        mock_icp.withdraw.assert_called_once_with("test_address")


def test_handle_v1_withdraw_post_has_approved_users():
    mock_db = MockDBClient()
    mock_icp = MockICPClient()
    init_mock_db_with_test_data(mock_db)

    token = create_jwt_token(data={"id": 1})

    mock_db.get_users = MagicMock(return_value={"users": [{"email": "user2@test.com"}]})
    mock_db.get_user = MagicMock(return_value={"is_approved": True})

    with patch('handlers.v1_withdraw.db', mock_db), \
         patch('handlers.v1_withdraw.icp', mock_icp):
        response = handle_v1_withdraw_post(token)

        assert isinstance(response, JSONResponse)
        assert response.status_code == 400
        assert b"insurer has approved users, cannot withdraw money" in response.body


def test_handle_v1_withdraw_post_invalid_token():
    mock_db = MockDBClient()
    mock_icp = MockICPClient()

    with patch('handlers.v1_withdraw.db', mock_db), \
         patch('handlers.v1_withdraw.icp', mock_icp):
        response = handle_v1_withdraw_post("invalid_token")

        assert isinstance(response, JSONResponse)
        assert response.status_code == 500
        assert b"message" in response.body


def test_handle_v1_withdraw_post_server_error():
    mock_db = MockDBClient()
    mock_icp = MockICPClient()
    init_mock_db_with_test_data(mock_db)

    token = create_jwt_token(data={"id": 1})

    def raise_error(*args, **kwargs):
        raise Exception("Database error")

    mock_db.get_users = raise_error

    with patch('handlers.v1_withdraw.db', mock_db), \
         patch('handlers.v1_withdraw.icp', mock_icp):
        response = handle_v1_withdraw_post(token)

        assert isinstance(response, JSONResponse)
        assert response.status_code == 500
        assert b"Database error" in response.body
