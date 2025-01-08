from pydantic import BaseModel


class GetSchemasRequest(BaseModel):
    company_id: int


class GetSchemaRequest(BaseModel):
    global_scheme_version: int
