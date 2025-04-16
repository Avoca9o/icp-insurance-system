from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse

from clients import db_client, icp_client
from utils.jwt import oauth2_scheme, decode_jwt_token

router = APIRouter()

db = db_client.DBClient()
icp = icp_client.ICPClient()


@router.get("/v1/balance")
def handle_v1_balance_request(token: str = Depends(oauth2_scheme)):
    try:
        company_id = decode_jwt_token(token)

        company = db.get_company(company_id)

        if not company:
            raise ValueError(f"Company does not exist")
        
        content = {"message": f"Your balance is {icp.get_balance(company.pay_address)} rubles"}
        return JSONResponse(content=content, status_code=200)
    except ValueError as e:
        return JSONResponse(content={"message": str(e)}, status_code=400)
    except Exception as e:
        return JSONResponse(content={"message": str(e)}, status_code=500)