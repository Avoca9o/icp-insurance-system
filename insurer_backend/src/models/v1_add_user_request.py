from pydantic import BaseModel

from entities.user_info import UserInfo


class AddUserRequest(BaseModel):
    phone: str
    insurance_amount: int
    payout_address: str
    insurer_id: int
    schema_version: int
    secondary_filters: dict = {}

    def check_validity(self):
        if self.phone is None or len(self.phone) == 0:
            raise ValueError("Phone number name cannot be empty")

        if self.payout_address is None or len(self.payout_address) == 0:
            raise ValueError("Payout address name cannot be empty")

    def as_user_info(self):
        return UserInfo(phone=self.phone,
                        insurance_amount=self.insurance_amount,
                        payout_address=self.payout_address,
                        insurer_id=self.insurer_id,
                        schema_version=self.schema_version,
                        secondary_filters=str(self.secondary_filters))
