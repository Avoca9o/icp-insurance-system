from fastapi import APIRouter, Depends, UploadFile, File
from fastapi.responses import JSONResponse

from pydantic import BaseModel

from clients import db_client
from entities.insurer_scheme import InsurerScheme
from utils.jwt import oauth2_scheme, decode_jwt_token
from utils.logger import logger

import pandas as pd

router = APIRouter()

db = db_client.DBClient()


class AddSchemaRequest(BaseModel):
    diagnoses_coefs: str

    def as_insurer_scheme(self, company_id: int):
        return InsurerScheme(company_id=company_id, diagnoses_coefs=self.diagnoses_coefs)


@router.post("/v1/add-scheme")
def handle_v1_add_scheme(req: AddSchemaRequest, token: str = Depends(oauth2_scheme)):
    try:
        company_id = decode_jwt_token(token)
        db.add_scheme(req.as_insurer_scheme(company_id))

        return JSONResponse(content=None, status_code=200)
    except ValueError as e:
        return JSONResponse(content={"message": str(e)}, status_code=400)
    except Exception as e:
        return JSONResponse(content={"message": str(e)}, status_code=500)


@router.post("/v1/add-scheme-csv")
def handle_v1_add_scheme_csv(file: UploadFile = File(...), token: str = Depends(oauth2_scheme)):
    try:
        if file.content_type != 'text/csv':
            raise ValueError("Invalid file format. CSV required")

        file.file.seek(0)

        df = pd.read_csv(file.file)
        result_dict = pd.Series(df.Coefficient.values, index=df.Code).to_dict()
        logger.info(result_dict)
        company_id = decode_jwt_token(token)
        db.add_scheme(InsurerScheme(diagnoses_coefs=str(result_dict).replace("'", '"'), company_id=company_id))
        return JSONResponse(content=None, status_code=200)
    except ValueError as e:
        return JSONResponse(content={"message": str(e)}, status_code=400)
    except Exception as e:
        return JSONResponse(content={"message": str(e)}, status_code=500)
