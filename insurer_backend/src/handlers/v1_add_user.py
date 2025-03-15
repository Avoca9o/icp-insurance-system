from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse

from clients import db_client
from utils.jwt import oauth2_scheme, decode_jwt_token

from pydantic import BaseModel

from entities.user_info import UserInfo

router = APIRouter()

db = db_client.DBClient()


def check_secondary_filters(filters):
    if not isinstance(filters, dict):
        raise ValueError("Secondary filters is not a dictionary")
    if not all(
        isinstance(k, str) and isinstance(v, float)
        for k, v in filters.items()
    ):
        raise ValueError("Secondary filters must be a dictionary of <string>:<float>")


class AddUserRequest(BaseModel):
    email: str
    insurance_amount: int
    schema_version: int
    secondary_filters: dict = {}

    def check_validity(self):
        if self.email is None or len(self.email) == 0:
            raise ValueError("Phone number name cannot be empty")
        check_secondary_filters(self.secondary_filters)

    def as_user_info(self, insurer_id):
        return UserInfo(email=self.email,
                        insurance_amount=self.insurance_amount,
                        insurer_id=insurer_id,
                        schema_version=self.schema_version,
                        secondary_filters=str(self.secondary_filters))


@router.post("/v1/add-user")
def handle_v1_add_user(req: AddUserRequest, token: str = Depends(oauth2_scheme)):
    try:
        company_id = decode_jwt_token(token)
        req.check_validity()

        db.add_user(req.as_user_info(company_id))

        return JSONResponse(content=None, status_code=200)
    except ValueError as e:
        return JSONResponse(content={"message": str(e)}, status_code=400)
    except Exception as e:
        print(str(e))
        return JSONResponse(content={"message": str(e)}, status_code=500)