from pydantic import BaseModel


class GetOperationsRequest(BaseModel):
    company: str
    date: str

    def check_validity(self):
        if self.company is None or len(self.company) == 0:
            raise ValueError("Company name cannot be empty")
        if self.date is None or len(self.date) == 0:
            raise ValueError("Date cannot be empty")
