from fastapi import APIRouter
from fastapi.responses import JSONResponse

from clients import db_client
from utils.jwt import create_jwt_token

from pydantic import BaseModel

router = APIRouter()
db = db_client.DBClient()


class AuthorizationRequest(BaseModel):
    login: str
    password: str

    def check_validity(self):
        if self.login is None or len(self.login) == 0:
            raise ValueError("login should not be empty")

        if self.password is None or len(self.password) == 0:
            raise ValueError("password should not be empty")


@router.post("/v1/authorize")
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