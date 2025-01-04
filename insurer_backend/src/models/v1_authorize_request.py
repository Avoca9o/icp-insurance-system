from pydantic import BaseModel


class AuthorizationRequest(BaseModel):
    login: str
    password: str

    def check_validity(self):
        if self.login is None or len(self.login) == 0:
            raise ValueError("login should not be empty")

        if self.password is None or len(self.password) == 0:
            raise ValueError("password should not be empty")
