from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse

from clients import db_client
from utils.jwt import oauth2_scheme

from pydantic import BaseModel

from entities.user_info import UserInfo

router = APIRouter()

db = db_client.DBClient()


class UpdateUserRequest(BaseModel):
    email: str
    insurer_schema: int = None
    secondary_filters: dict = {}

    def check_validity(self):
        if self.email is None or len(self.email) == 0:
            raise ValueError("Phone number name cannot be empty in update user request")

    def as_user_info(self):
        return UserInfo(email=self.email,
                        secondary_filters=str(self.secondary_filters),
                        schema_version=self.insurer_schema)


@router.post("/v1/update-user")
def handle_v1_update_user(req: UpdateUserRequest, token: str = Depends(oauth2_scheme)):
    try:
        req.check_validity()

        db.update_user(req.as_user_info())

        return JSONResponse(content=None, status_code=200)
    except ValueError as e:
        return JSONResponse(content={"message": str(e)}, status_code=400)
    except Exception as e:
        return JSONResponse(content={"message": str(e)}, status_code=500)