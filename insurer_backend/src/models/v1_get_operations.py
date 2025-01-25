from pydantic import BaseModel


class GetOperationsRequest(BaseModel):
    company_id: int
    date: str

    def check_validity(self):
        if self.date is None or len(self.date) == 0:
            raise ValueError("Date cannot be empty")
