from pydantic import BaseModel

from entities.user_info import UserInfo


class AddUserRequest(BaseModel):
    email: str
    insurance_amount: int
    schema_version: int
    secondary_filters: dict = {}

    def check_validity(self):
        if self.email is None or len(self.email) == 0:
            raise ValueError("Phone number name cannot be empty")

    def as_user_info(self, insurer_id):
        return UserInfo(email=self.email,
                        insurance_amount=self.insurance_amount,
                        insurer_id=insurer_id,
                        schema_version=self.schema_version,
                        secondary_filters=str(self.secondary_filters))
