from pydantic import BaseModel

from entities.insurer_scheme import InsurerScheme

from typing import List


class AddSchemaRequest(BaseModel):
    diagnoses_coefs: str

    def as_insurer_scheme(self, company_id: int):
        return InsurerScheme(company_id=company_id, diagnoses_coefs=self.diagnoses_coefs)
