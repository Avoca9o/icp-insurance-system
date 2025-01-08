from pydantic import BaseModel

from entities.user_info import UserInfo


class UpdateUserRequest(BaseModel):
    phone_number: str
    payout_address: str = None
    insurer_login: str = None
    insurer_schema: int = None
    secondary_filters: dict = {}

    def check_validity(self):
        if self.phone_number is None or len(self.phone_number) == 0:
            raise ValueError("Phone number name cannot be empty in update user request")

    def as_user_info(self):
        return UserInfo(phone=self.phone_number,
                        payout_address=self.payout_address,
                        insurer=self.insurer_login,
                        secondary_filters=str(self.secondary_filters),
                        schema=self.insurer_schema)
