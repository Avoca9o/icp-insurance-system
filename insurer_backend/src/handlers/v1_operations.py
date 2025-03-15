from fastapi import APIRouter, Depends, Response
from fastapi.responses import JSONResponse

from pydantic import BaseModel

from clients import db_client
from entities.insurer_scheme import InsurerScheme
from utils.jwt import oauth2_scheme, decode_jwt_token
from pydantic import BaseModel
from io import StringIO

import pandas as pd


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

        data = {
            "User": [x['user'] for x in res],
            "Amount": [x['amount'] for x in res],
            "Date": [x['date'] for x in res]
        }
        df = pd.DataFrame(data)

        csv_buffer = StringIO()
        df.to_csv(csv_buffer, index=False, encoding='utf-8')

        return Response(content=csv_buffer.getvalue(), media_type="text/csv",
                    headers={"Content-Disposition": "attachment; filename=data.csv"})
    except ValueError as e:
        return JSONResponse(content={"message": str(e)}, status_code=400)
    except Exception as e:
        return JSONResponse(content={"message": str(e)}, status_code=500)
