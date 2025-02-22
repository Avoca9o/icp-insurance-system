from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse

from pydantic import BaseModel

from clients import db_client
from entities.insurer_scheme import InsurerScheme
from utils.jwt import oauth2_scheme, decode_jwt_token
from pydantic import BaseModel


router = APIRouter()

db = db_client.DBClient()


class GetOperationsRequest(BaseModel):
    company_id: int
    date: str

    def check_validity(self):
        if self.date is None or len(self.date) == 0:
            raise ValueError("Date cannot be empty")


@router.get("/v1/operations")
def handle_v1_operations(date: str, token: str = Depends(oauth2_scheme)):
    try:
        company_id = decode_jwt_token(token)
        res = db.get_payouts_by_company_and_date(company_id, date)

        return JSONResponse(content={'operations': res}, status_code=200)
    except ValueError as e:
        return JSONResponse(content={"message": str(e)}, status_code=400)
    except Exception as e:
        return JSONResponse(content={"message": str(e)}, status_code=500)
