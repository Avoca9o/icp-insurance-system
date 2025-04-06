from typing import Dict, List, Optional
from entities.company_info import CompanyInfo
from entities.user_info import UserInfo
from entities.insurer_scheme import InsurerScheme
from entities.payout import Payout


class MockDBClient:
    def __init__(self):
        self.companies: Dict[int, CompanyInfo] = {}
        self.users: Dict[str, UserInfo] = {}
        self.schemes: Dict[int, InsurerScheme] = {}
        self.payouts: List[Payout] = []
        self.next_company_id = 1
        self.next_scheme_id = 1

    def add_company(self, company: CompanyInfo) -> None:
        # Проверяем существование логина
        for existing_company in self.companies.values():
            if existing_company.login == company.login:
                raise ValueError(f"company with login {company.login} already exists")

        # Добавляем компанию
        company.id = self.next_company_id
        self.companies[self.next_company_id] = company
        self.next_company_id += 1

    def get_company(self, comp_id: int) -> Optional[CompanyInfo]:
        return self.companies.get(comp_id)

    def authorize_company(self, login: str, password: str) -> int:
        # Ищем компанию по логину
        for company in self.companies.values():
            if company.login == login:
                if company.password == password:
                    return company.id
                raise ValueError("Invalid password")
        raise ValueError("No such login exists")

    def add_user(self, user: UserInfo) -> None:
        if user.email in self.users:
            raise ValueError(f"user with phone number {user.email} already exists")
        self.users[user.email] = user

    def update_user(self, user: UserInfo, company_id: int) -> None:
        if user.email not in self.users:
            raise ValueError(f"user with email {user.email} not exists")

        db_user = self.users[user.email]
        if db_user.insurer_id != company_id:
            raise ValueError(f"user with email {user.email} is not in company's users list")

        if db_user.is_approved:
            raise ValueError(f"user with email {user.email} has already approved his info, can't change info")

        # Обновляем только указанные поля
        if user.insurance_amount is not None:
            db_user.insurance_amount = user.insurance_amount
        if user.schema_version is not None:
            db_user.schema_version = user.schema_version
        if user.secondary_filters is not None:
            db_user.secondary_filters = user.secondary_filters

    def add_scheme(self, scheme: InsurerScheme) -> None:
        scheme.id = self.next_scheme_id
        self.schemes[self.next_scheme_id] = scheme
        self.next_scheme_id += 1

    def get_schemas(self, company_id: int) -> List[InsurerScheme]:
        return [scheme for scheme in self.schemes.values() if scheme.company_id == company_id]

    def get_schema(self, global_scheme_version: int) -> Optional[InsurerScheme]:
        return self.schemes.get(global_scheme_version)

    def get_users(self, company_id: int) -> List[UserInfo]:
        return [user for user in self.users.values() if user.insurer_id == company_id]

    def get_user(self, email: str, company_id: int) -> Optional[UserInfo]:
        user = self.users.get(email)
        if user and user.insurer_id == company_id:
            return user
        return None

    def delete_user(self, email: str, company_id: int) -> None:
        user = self.get_user(email, company_id)
        if not user:
            raise ValueError(f"user with email {email} not exists")
        del self.users[email]

    def get_payouts_by_company_and_date(self, company_id: int, target_date: str) -> List[Payout]:
        return [payout for payout in self.payouts 
                if payout.insurer_id == company_id and payout.date == target_date] 