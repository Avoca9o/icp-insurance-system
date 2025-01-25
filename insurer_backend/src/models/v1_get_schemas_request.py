from pydantic import BaseModel


class GetSchemaRequest(BaseModel):
    global_scheme_version: int
