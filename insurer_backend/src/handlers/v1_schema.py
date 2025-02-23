from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse

import json

from pydantic import BaseModel

from clients import db_client
from entities.insurer_scheme import InsurerScheme
from utils.jwt import oauth2_scheme, decode_jwt_token

router = APIRouter()

db = db_client.DBClient()



@router.get("/v1/schema")
def handle_v1_schema(global_version_id: int, token: str = Depends(oauth2_scheme)):
    try:
        company_id = decode_jwt_token(token)

        res = db.get_schema(global_version_id)

        if res.company_id != company_id:
            raise ValueError("schema is not for that company")

        dc = str(json.loads(res.diagnoses_coefs))
        dc = dc.replace("'", '"')
        return JSONResponse(content={'scheme': dc}, status_code=200)
    except ValueError as e:
        print(str(e))
        return JSONResponse(content={"message": str(e)}, status_code=400)
    except Exception as e:
        return JSONResponse(content={"message": str(e)}, status_code=500)