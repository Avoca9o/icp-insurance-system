from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse

from clients import icp_client, db_client

from utils.jwt import oauth2_scheme, decode_jwt_token

router = APIRouter()

icp = icp_client.ICPClient()
db = db_client.DBClient()


@router.post("/v1/withdraw")
def handle_v1_withdraw_post(token: str = Depends(oauth2_scheme)):
    try:
        company_id = decode_jwt_token(token)
        insurer = db.get_company(company_id)

        users = db.get_users(company_id)['users']
        for user in users:
            db_user = db.get_user(user["email"], company_id)
            if db_user['is_approved']:
                raise ValueError('insurer has approved users, cannot withdraw money')

        icp.withdraw(insurer.pay_address)
        print("money withdrew successfully")
        return JSONResponse(content=None, status_code=200)
    except ValueError as e:
        return JSONResponse(content={"message": str(e)}, status_code=400)
    except Exception as e:
        return JSONResponse(content={"message": str(e)}, status_code=500)