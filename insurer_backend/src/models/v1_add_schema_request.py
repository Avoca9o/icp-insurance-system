from pydantic import BaseModel

from entities.insurer_scheme import InsurerScheme

from typing import List


class DiagnosesCoef(BaseModel):
    diagnoses: str
    coef: float


class AddSchemaRequest(BaseModel):
    company_id: int
    diagnoses_coefs: List[DiagnosesCoef]

    def as_insurer_scheme(self):
        d_coefs = [{"diagnoses": x.diagnoses, "coef": x.coef} for x in self.diagnoses_coefs]
        return InsurerScheme(company_id=self.company_id, diagnoses_coefs=str(d_coefs))
