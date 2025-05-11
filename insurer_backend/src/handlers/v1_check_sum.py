from fastapi import APIRouter, Depends

from fastapi.responses import JSONResponse

from pydantic import BaseModel
from clients import db_client, icp_client

from utils.check_sum import checksum
from utils.jwt import oauth2_scheme, decode_jwt_token
from utils.logger import logger

router = APIRouter()

db = db_client.DBClient()
icp = icp_client.ICPClient()


@router.get("/v1/check-sum")
def handle_v1_check_sum(email: str, token: str = Depends(oauth2_scheme)):
    try:
        company_id = decode_jwt_token(token)

        user = db.get_user(email, company_id)

        if not user["is_approved"]:
            raise ValueError("can't validate check sum while user's contract is not approved")

        schema = db.get_schema(user['scheme_version'])

        check_sum = checksum(str(schema), str(user['secondary_filters']))

        return JSONResponse(content={"is_valid": icp.is_checksum_valid(company_id, user['telegram_id'], check_sum)},
                            status_code=200)

    except ValueError as e:
        return JSONResponse(content={"message": str(e)}, status_code=400)
    except Exception as e:
        logger.error(str(e))
        return JSONResponse(content={"message": str(e)}, status_code=500)
