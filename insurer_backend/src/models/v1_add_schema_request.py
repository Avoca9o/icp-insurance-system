from pydantic import BaseModel

from entities.insurer_scheme import InsurerScheme

from typing import List


class DiagnosesCoef(BaseModel):
    diagnoses: str
    coef: float


class AddSchemaRequest(BaseModel):
    diagnoses_coefs: List[DiagnosesCoef]

    def as_insurer_scheme(self, company_id: int):
        d_coefs = [{"diagnoses": x.diagnoses, "coef": x.coef} for x in self.diagnoses_coefs]
        return InsurerScheme(company_id=company_id, diagnoses_coefs=str(d_coefs))
