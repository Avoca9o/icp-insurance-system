from pydantic import BaseModel

from entities.user_info import UserInfo


class AddUserRequest(BaseModel):
    phone_number: str
    payout_address: str
    insurer_login: str
    insurer_schema: int
    secondary_filters: dict = {}

    def check_validity(self):
        if self.phone_number is None or len(self.phone_number) == 0:
            raise ValueError("Phone number name cannot be empty")

        if self.payout_address is None or len(self.payout_address) == 0:
            raise ValueError("Payout address name cannot be empty")

        if self.insurer_login is None or len(self.insurer_login) == 0:
            raise ValueError("Insurer login name cannot be empty")

        if self.insurer_schema is None:
            raise ValueError("Insurer schema name cannot be empty")

    def as_user_info(self):
        return UserInfo(phone=self.phone_number,
                        payout_address=self.payout_address,
                        insurer=self.insurer_login,
                        secondary_filters=str(self.secondary_filters),
                        schema=self.insurer_schema)
