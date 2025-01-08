from fastapi import FastAPI
from fastapi.responses import JSONResponse

import clients.icp_client as icp_client
import clients.db_client as db_client

import models.v1_get_balance_request as get_balance_request
import models.v1_withdraw_request as withdraw_request
from models.v1_register_request import RegisterRequest
from models.v1_authorize_request import AuthorizationRequest
from models.v1_add_user_request import AddUserRequest
from models.v1_update_user_request import UpdateUserRequest

from config.db_config import engine

db_client.Base.metadata.create_all(bind=engine)

app = FastAPI()

icp = icp_client.ICPClient()
db = db_client.DBClient()


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
        db.authorize_company(req.login, req.password)
        # TODO: sessions and tokens
        return JSONResponse(content=None, status_code=200)
    except ValueError as e:
        return JSONResponse(content={"message": str(e)}, status_code=400)
    except Exception as e:
        return JSONResponse(content={"message": str(e)}, status_code=500)


# Returns the icppp smart contract address
@app.get("/v1/get-icp-address")
def handle_v1_get_icp_address():
    content = {"message": icp_client.MAIN_ADDRESS}
    return JSONResponse(content=content, status_code=200)


# Returns company's amount of money in the system
@app.get("/v1/get-balance")
def handle_v1_get_balance_request(req: get_balance_request.GetBalanceRequest):
    try:
        req.check_validity()
        # TODO: проверить наличие компании в базе данных (хотя мб и не надо)

        content = {"message": f"Your balance is {icp.get_balance(req.company)} dirhum"}
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
def handle_v1_operations():
    content = {"message": {"operations": [
        {"to_address": "444.333.222", "amount": 100, "date": "2025-01-01"},
        {"to_address": "445.333.222", "amount": 200, "date": "2025-01-02"},
        {"to_address": "446.333.222", "amount": 3100, "date": "2025-01-01"},
    ]}}
    return JSONResponse(content=content, status_code=200)


# Adds user to company's database (maybe we should use unique contract id)
@app.post("/v1/add-user")
def handle_v1_add_user(req: AddUserRequest):
    try:
        req.check_validity()

        db.add_user(req.as_user_info())

        return JSONResponse(content=None, status_code=200)
    except ValueError as e:
        return JSONResponse(content={"message": str(e)}, status_code=400)
    except Exception as e:
        return JSONResponse(content={"message": str(e)}, status_code=500)


# Update secondary filters or personal info if not blocked (can be blocked by user via tg bot)
@app.post("/v1/update-user")
def handle_v1_update_user(req: UpdateUserRequest):
    try:
        req.check_validity()

        db.update_user(req.as_user_info())

        return JSONResponse(content=None, status_code=200)
    except ValueError as e:
        return JSONResponse(content={"message": str(e)}, status_code=400)
    except Exception as e:
        return JSONResponse(content={"message": str(e)}, status_code=500)
