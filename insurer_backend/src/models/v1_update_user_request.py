from pydantic import BaseModel

from entities.user_info import UserInfo


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
