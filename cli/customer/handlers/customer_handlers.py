# cli/customer/handlers/customer_handlers.py

from typing import Optional
from sqlalchemy.orm import Session

from cli.common.base_handler import BaseHandler
from services import CustomerService, DisplayService


class SelectCustomerHandler(BaseHandler):
    def __init__(self, session: Session):
        super().__init__(session)
        self._customer_service = CustomerService()
        self._display_service = DisplayService()

    def handle(self) -> Optional[str]:
        self._display_header("ВЫБОР КЛИЕНТА")

        customers = self._customer_service.get_all_customers(self._session)
        if not customers:
            print("❌ Клиенты не найдены")
            self._wait()
            return None

        print(self._display_service.format_customers(customers))
        print("\n0. Отмена")

        choice = self._input_choice("\nВыберите клиента (номер): ", len(customers))
        if choice is None or choice == 0:
            return None

        customer = customers[choice - 1]
        print(f"\n✅ Выбран клиент: {customer.company_name}")
        self._wait()
        return customer.customer_id