from pydantic import BaseModel

from entities.company_info import CompanyInfo


class RegisterRequest(BaseModel):
    login: str
    password: str
    name: str
    email: str
    pay_address: str

    def check_validity(self):
        if self.login is None or len(self.login) == 0:
            raise ValueError("login should not be empty")

        if self.name is None or len(self.name) == 0:
            raise ValueError("name should not be empty")

        if self.email is None or len(self.email) == 0:
            raise ValueError("email should not be empty")

        if self.password is None or len(self.password) == 0:
            raise ValueError("password should not be empty")

        if self.pay_address is None or len(self.pay_address) == 0:
            raise ValueError("pay_address should not be empty")

    def as_company_info(self):
        return CompanyInfo(self.login, self.password, self.name, self.email, self.pay_address)
