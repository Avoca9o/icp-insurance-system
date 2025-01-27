import json
from fastapi import FastAPI, Depends
from fastapi.responses import JSONResponse

import clients.icp_client as icp_client
import clients.db_client as db_client

import models.v1_withdraw_request as withdraw_request
from models.v1_register_request import RegisterRequest
from models.v1_authorize_request import AuthorizationRequest
from models.v1_add_user_request import AddUserRequest
from models.v1_update_user_request import UpdateUserRequest
from models.v1_add_schema_request import AddSchemaRequest
from models.v1_get_operations import GetOperationsRequest

from config.db_config import engine
from fastapi.middleware.cors import CORSMiddleware

from jose import jwt
from fastapi.security import OAuth2PasswordBearer

SECRET_KEY = "your_secret_key"
ALGORITHM = "HS256"

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/v1/authorize")


def create_jwt_token(data: dict):
    to_encode = data.copy()
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def decode_jwt_token(token):
    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    return payload.get("id")


db_client.Base.metadata.create_all(bind=engine)

app = FastAPI()

icp = icp_client.ICPClient()
db = db_client.DBClient()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/ping")
def handle_ping():
    content = {"message": "Hello world"}
    return JSONResponse(content=content, status_code=200)


@app.get("/check-db")
def check_db_connection():
    try:
        content = db_client.execute_query()
        return JSONResponse(content=content, status_code=200)
    except Exception as e:
        return JSONResponse(content=str(e), status_code=500)


@app.get("/check-canister-health")
def check_canister_health():
    try:
        icp.check_canister_health()
        return JSONResponse(content=None, status_code=200)
    except Exception as e:
        return JSONResponse(content={"message": str(e)}, status_code=500)


# Adds insurance company to system with unique names
@app.post("/v1/register")
def handle_v1_register(req: RegisterRequest):
    try:
        req.check_validity()
        icp.register_company(req.pay_address)
        db.add_company(req.as_company_info())
        return JSONResponse(content=None, status_code=200)
    except ValueError as e:
        return JSONResponse(content={"message": str(e)}, status_code=400)
    except Exception as e:
        return JSONResponse(content={"message": str(e)}, status_code=500)


# Tries to authorize insurance company
@app.post("/v1/authorize")
def handle_v1_authorize(req: AuthorizationRequest):
    try:
        req.check_validity()
        company_id = db.authorize_company(req.login, req.password)

        token = create_jwt_token(data={"id": company_id})

        return JSONResponse(content={"access_token": token}, status_code=200)
    except ValueError as e:
        return JSONResponse(content={"message": str(e)}, status_code=400)
    except Exception as e:
        return JSONResponse(content={"message": str(e)}, status_code=500)


@app.get("/v1/get-icp-address")
def handle_v1_get_icp_address(token: str = Depends(oauth2_scheme)):
    content = {"icp_address": icp_client.CANISTER_ID}
    return JSONResponse(content=content, status_code=200)


# Returns company's amount of money in the system
@app.get("/v1/get-balance")
def handle_v1_get_balance_request(token: str = Depends(oauth2_scheme)):
    try:
        company_id = decode_jwt_token(token)

        company = db.get_company(company_id)

        if not company:
            raise ValueError(f"Company does not exist")

        content = {"message": f"Your balance is {icp.get_balance(company.pay_address)} dirhum"}
        return JSONResponse(content=content, status_code=200)
    except ValueError as e:
        return JSONResponse(content={"message": str(e)}, status_code=400)
    except Exception as e:
        return JSONResponse(content={"message": str(e)}, status_code=500)


# Make request to withdraw all company's money from smart contract (available only if the lifetime is exceeded)
@app.post("/v1/withdraw")
def handle_v1_withdraw(req: withdraw_request.WithdrawRequest):
    try:
        req.check_validity()
        # TODO: check company's number of clients, if there're some of them there cannot be an opportunity to withdraw
        icp.withdraw(req.company)
        return JSONResponse(content=None, status_code=200)
    except ValueError as e:
        return JSONResponse(content={"message": str(e)}, status_code=400)
    except Exception as e:
        return JSONResponse(content={"message": str(e)}, status_code=500)


# Returns the list of operations clients of certain company done
@app.get("/v1/operations")
def handle_v1_operations(token: str = Depends(oauth2_scheme)):
    content = {"message": {"operations": [
        {"to_address": "444.333.222", "amount": 100, "date": "2025-01-01"},
        {"to_address": "445.333.222", "amount": 200, "date": "2025-01-02"},
        {"to_address": "446.333.222", "amount": 3100, "date": "2025-01-01"},
    ]}}
    return JSONResponse(content=content, status_code=200)


# Adds user to company's database (maybe we should use unique contract id)
@app.post("/v1/add-user")
def handle_v1_add_user(req: AddUserRequest, token: str = Depends(oauth2_scheme)):
    try:
        company_id = decode_jwt_token(token)
        req.check_validity()

        db.add_user(req.as_user_info(company_id))

        return JSONResponse(content=None, status_code=200)
    except ValueError as e:
        return JSONResponse(content={"message": str(e)}, status_code=400)
    except Exception as e:
        print(str(e))
        return JSONResponse(content={"message": str(e)}, status_code=500)


# Update secondary filters or personal info if not blocked (can be blocked by user via tg bot)
@app.post("/v1/update-user")
def handle_v1_update_user(req: UpdateUserRequest, token: str = Depends(oauth2_scheme)):
    try:
        req.check_validity()

        db.update_user(req.as_user_info())

        return JSONResponse(content=None, status_code=200)
    except ValueError as e:
        return JSONResponse(content={"message": str(e)}, status_code=400)
    except Exception as e:
        return JSONResponse(content={"message": str(e)}, status_code=500)


@app.get("/v1/get-users")
def handle_v1_get_users(token: str = Depends(oauth2_scheme)):
    try:
        company_id = decode_jwt_token(token)
        res = db.get_users(company_id)

        return JSONResponse(content=res, status_code=200)
    except ValueError as e:
        return JSONResponse(content={"message": str(e)}, status_code=400)
    except Exception as e:
        return JSONResponse(content={"message": str(e)}, status_code=500)


@app.get("/v1/get-user")
def handle_v1_get_users(email: str, token: str = Depends(oauth2_scheme)):
    try:
        company_id = decode_jwt_token(token)

        res = db.get_user(email, company_id)

        return JSONResponse(content={'user': res}, status_code=200)
    except ValueError as e:
        return JSONResponse(content={"message": str(e)}, status_code=400)
    except Exception as e:
        print(str(e))
        return JSONResponse(content={"message": str(e)}, status_code=500)


@app.delete("/v1/delete-user")
def handle_v1_delete_user(email: str, token: str = Depends(oauth2_scheme)):
    try:
        company_id = decode_jwt_token(token)

        db.delete_user(email, company_id)

        return JSONResponse(content=None, status_code=200)
    except ValueError as e:
        return JSONResponse(content={"message": str(e)}, status_code=400)
    except Exception as e:
        print(str(e))
        return JSONResponse(content={"message": str(e)}, status_code=500)


@app.post("/v1/add-scheme")
def handle_v1_add_scheme(req: AddSchemaRequest, token: str = Depends(oauth2_scheme)):
    try:
        company_id = decode_jwt_token(token)
        db.add_scheme(req.as_insurer_scheme(company_id))

        return JSONResponse(content=None, status_code=200)
    except ValueError as e:
        return JSONResponse(content={"message": str(e)}, status_code=400)
    except Exception as e:
        return JSONResponse(content={"message": str(e)}, status_code=500)


@app.get("/v1/get-schemas")
def handle_v1_get_schemas(token: str = Depends(oauth2_scheme)):
    try:
        company_id = decode_jwt_token(token)
        res = db.get_schemas(company_id)
        return JSONResponse(content=res, status_code=200)
    except ValueError as e:
        return JSONResponse(content={"message": str(e)}, status_code=400)
    except Exception as e:
        return JSONResponse(content={"message": str(e)}, status_code=500)


@app.get("/v1/get-schema")
def handle_v1_get_schema(global_version_id: int, token: str = Depends(oauth2_scheme)):
    try:
        company_id = decode_jwt_token(token)

        res = db.get_schema(global_version_id)

        if res.company_id != company_id:
            raise ValueError("schema is not for that company")

        dc = res.diagnoses_coefs
        dc = dc.replace("'", '"')
        return JSONResponse(content={'scheme': json.loads(dc)}, status_code=200)
    except ValueError as e:
        print(str(e))
        return JSONResponse(content={"message": str(e)}, status_code=400)
    except Exception as e:
        return JSONResponse(content={"message": str(e)}, status_code=500)


@app.get("/v1/get-operations")
def handle_v1_get_operations(date: str, token: str = Depends(oauth2_scheme)):
    try:
        company_id = decode_jwt_token(token)
        res = db.get_payouts_by_company_and_date(company_id, date)

        return JSONResponse(content={'operations': res}, status_code=200)
    except ValueError as e:
        return JSONResponse(content={"message": str(e)}, status_code=400)
    except Exception as e:
        return JSONResponse(content={"message": str(e)}, status_code=500)
