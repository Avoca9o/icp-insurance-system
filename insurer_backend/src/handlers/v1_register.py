from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse

from pydantic import BaseModel

from clients import db_client, icp_client
from entities.insurer_scheme import InsurerScheme
from utils.jwt import oauth2_scheme, decode_jwt_token
from utils.logger import logger

from pydantic import BaseModel

from entities.company_info import CompanyInfo

router = APIRouter()

db = db_client.DBClient()
icp = icp_client.ICPClient()


class RegisterRequest(BaseModel):
    login: str
    password: str
    name: str
    email: str
    pay_address: str

    def check_validity(self):
        if self.login is None or len(self.login) == 0:
            raise ValueError("login should not be empty")

        if self.name is None or len(self.name) == 0:
            raise ValueError("name should not be empty")

        if self.email is None or len(self.email) == 0:
            raise ValueError("email should not be empty")

        if self.password is None or len(self.password) == 0:
            raise ValueError("password should not be empty")

        if self.pay_address is None or len(self.pay_address) == 0:
            raise ValueError("pay_address should not be empty")

    def as_company_info(self):
        return CompanyInfo(self.login, self.password, self.name, self.email, self.pay_address)


@router.post("/v1/register")
def handle_v1_register(req: RegisterRequest):
    try:
        req.check_validity()
        icp.register_company(req.pay_address)
        db.add_company(req.as_company_info())
        return JSONResponse(content=None, status_code=200)
    except ValueError as e:
        return JSONResponse(content={"message": str(e)}, status_code=400)
    except Exception as e:
        logger.error(str(e))
        return JSONResponse(content={"message": str(e)}, status_code=500)