from pydantic import BaseModel


class WithdrawRequest(BaseModel):
    company: str

    def check_validity(self):
        if self.company is None or len(self.company) == 0:
            raise ValueError("Company name cannot be empty")
