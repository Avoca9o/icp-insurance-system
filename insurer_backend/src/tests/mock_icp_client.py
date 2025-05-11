from typing import Dict, Optional
import random

from utils.logger import logger

class MockICPClient:
    def __init__(self):
        # Хранилище балансов компаний
        self.balances: Dict[str, float] = {}
        # Хранилище зарегистрированных компаний
        self.registered_companies: set[str] = set()
        # Хранилище валидных чек-сумм
        self.valid_checksums: set[tuple[int, int, str]] = set()
        # Флаг состояния canister'а
        self.canister_healthy: bool = True

    def get_balance(self, company_pay_address: str) -> float:
        """
        Возвращает баланс компании.
        Если компания не зарегистрирована, возвращает 0.0
        """
        if company_pay_address not in self.registered_companies:
            raise Exception("Company is not registered")
        return self.balances.get(company_pay_address, 0.0)

    def withdraw(self, payout_address: str) -> None:
        """
        Выполняет вывод средств.
        Если компания не зарегистрирована или баланс равен 0, вызывает исключение.
        """
        if payout_address not in self.registered_companies:
            raise Exception("Company is not registered")
        
        balance = self.balances.get(payout_address, 0.0)
        if balance <= 0:
            raise Exception("Insufficient balance")
        
        self.balances[payout_address] = 0.0

    def check_canister_health(self) -> None:
        """
        Проверяет состояние canister'а.
        В тестовом режиме всегда возвращает True.
        """
        if not self.canister_healthy:
            raise Exception("Canister is not healthy")
        logger.info("Canister is alive")

    def register_company(self, payout_address: str) -> None:
        """
        Регистрирует компанию в canister'е.
        """
        if payout_address in self.registered_companies:
            raise Exception("Company already registered")
        
        self.registered_companies.add(payout_address)
        self.balances[payout_address] = 0.0
        logger.info('company is registered in canister')

    def is_checksum_valid(self, company_id: int, user_tg_id: int, current_sum: str) -> bool:
        """
        Проверяет валидность чек-суммы.
        В тестовом режиме можно настроить предопределенные результаты.
        """
        return (company_id, user_tg_id, current_sum) in self.valid_checksums

    # Вспомогательные методы для тестов
    def set_balance(self, payout_address: str, amount: float) -> None:
        """
        Устанавливает баланс для компании.
        """
        if payout_address not in self.registered_companies:
            raise Exception("Company is not registered")
        self.balances[payout_address] = amount

    def add_valid_checksum(self, company_id: int, user_tg_id: int, current_sum: str) -> None:
        """
        Добавляет валидную чек-сумму в хранилище.
        """
        self.valid_checksums.add((company_id, user_tg_id, current_sum))

    def set_canister_health(self, healthy: bool) -> None:
        """
        Устанавливает состояние canister'а.
        """
        self.canister_healthy = healthy 