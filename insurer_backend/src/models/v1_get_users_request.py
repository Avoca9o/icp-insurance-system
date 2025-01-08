from pydantic import BaseModel


class GetUsersRequest(BaseModel):
    company_id: int


class GetUserRequest(BaseModel):
    phone: str
