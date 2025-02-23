from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse

from clients import db_client
from utils.jwt import oauth2_scheme, decode_jwt_token

router = APIRouter()

db = db_client.DBClient()


@router.get("/v1/users")
def handle_v1_users_get(token: str = Depends(oauth2_scheme)):
    try:
        company_id = decode_jwt_token(token)
        res = db.get_users(company_id)

        return JSONResponse(content=res, status_code=200)
    except ValueError as e:
        return JSONResponse(content={"message": str(e)}, status_code=400)
    except Exception as e:
        return JSONResponse(content={"message": str(e)}, status_code=500)