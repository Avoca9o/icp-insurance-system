from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse

from clients import db_client
from utils.jwt import oauth2_scheme, decode_jwt_token

router = APIRouter()

db = db_client.DBClient()


@router.get("/v1/user")
def handle_v1_user_get(email: str, token: str = Depends(oauth2_scheme)):
    try:
        company_id = decode_jwt_token(token)

        res = db.get_user(email, company_id)

        return JSONResponse(content={'user': res}, status_code=200)
    except ValueError as e:
        return JSONResponse(content={"message": str(e)}, status_code=400)
    except Exception as e:
        print(str(e))
        return JSONResponse(content={"message": str(e)}, status_code=500)


@router.delete("/v1/user")
def handle_v1_user_delete(email: str, token: str = Depends(oauth2_scheme)):
    try:
        company_id = decode_jwt_token(token)

        db.delete_user(email, company_id)

        return JSONResponse(content=None, status_code=200)
    except ValueError as e:
        return JSONResponse(content={"message": str(e)}, status_code=400)
    except Exception as e:
        print(str(e))
        return JSONResponse(content={"message": str(e)}, status_code=500)