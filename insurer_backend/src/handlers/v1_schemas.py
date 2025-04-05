from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse

from clients import db_client
from utils.jwt import oauth2_scheme, decode_jwt_token

from pydantic import BaseModel


router = APIRouter()

db = db_client.DBClient()


class GetSchemaRequest(BaseModel):
    global_scheme_version: int


@router.get("/v1/schemas")
def handle_v1_schemas(token: str = Depends(oauth2_scheme)):
    try:
        company_id = decode_jwt_token(token)
        
        # Проверяем существование компании
        company = db.get_company(company_id)
        if not company:
            raise ValueError(f"Company does not exist")
        
        schemas = db.get_schemas(company_id)
        # Преобразуем схемы в список словарей
        schemas_data = [
            {
                "global_version_num": schema.global_version_num,
                "company_id": schema.company_id,
                "diagnoses_coefs": schema.diagnoses_coefs
            }
            for schema in schemas
        ]
        return JSONResponse(content=schemas_data, status_code=200)
    except ValueError as e:
        return JSONResponse(content={"message": str(e)}, status_code=400)
    except Exception as e:
        return JSONResponse(content={"message": str(e)}, status_code=500)