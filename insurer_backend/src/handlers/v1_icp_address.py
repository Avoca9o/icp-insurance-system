from fastapi import APIRouter, Depends

from fastapi.responses import JSONResponse

from utils.jwt import oauth2_scheme
from clients.icp_client import CANISTER_ID

router = APIRouter()


@router.get("/v1/icp-address")
def handle_v1_icp_address_get(token: str = Depends(oauth2_scheme)):
    content = {"icp_address": CANISTER_ID}
    return JSONResponse(content=content, status_code=200)