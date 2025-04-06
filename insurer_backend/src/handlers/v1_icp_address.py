from fastapi import APIRouter, Depends

from fastapi.responses import JSONResponse

from utils.jwt import oauth2_scheme, decode_jwt_token
from clients.icp_client import CANISTER_ID

router = APIRouter()


@router.get("/v1/icp-address")
def handle_v1_icp_address_get(token: str = Depends(oauth2_scheme)):
    try:
        decode_jwt_token(token)
        content = {"icp_address": CANISTER_ID}
        return JSONResponse(content=content, status_code=200)
    except Exception as e:
        return JSONResponse(content={"message": str(e)}, status_code=500)
