from fastapi import APIRouter
from fastapi.responses import JSONResponse

router = APIRouter()


@router.get("/ping")
def handle_ping():
    content = {"message": "Hello world"}
    return JSONResponse(content=content, status_code=200)