from typing import List, Optional, Tuple
from repositories.product_repository import ProductRepository
from repositories.shipper_repository import ShipperRepository

#TODO Correct the select_shipper for all available shippers ids
class InputHandler:
    def __init__(self, product_repo: ProductRepository, shipper_repo: ShipperRepository):
        self.product_repo = product_repo
        self.shipper_repo = shipper_repo

    def select_customer(self, customers: List) -> Optional:
        print("\n0. Выход")

        while True:
            try:
                choice = int(input("\nВыберите клиента (номер): "))
                if choice == 0:
                    return None
                if 1 <= choice <= len(customers):
                    return customers[choice - 1]
                print(f"❌ Введите число от 1 до {len(customers)}")
            except ValueError:
                print("❌ Введите корректный номер")

    def get_product_selection(self, products: List) -> Tuple[Optional, Optional]:
        while True:
            try:
                product_id = int(input("\nВведите ID товара (0 для выхода): "))
                if product_id == 0:
                    return None, None

                product = self.product_repo.get_by_id(product_id)
                if not product:
                    self._display_error("Товар не найден")
                    continue

                quantity = int(input(f"Введите количество (доступно: {product.units_in_stock}): "))
                if quantity <= 0:
                    self._display_error("Количество должно быть больше 0")
                    continue

                if quantity > product.units_in_stock:
                    self._display_error(f"Недостаточно товара. Доступно: {product.units_in_stock}")
                    continue

                return product, quantity

            except ValueError:
                self._display_error("Введите корректное число")

    def select_shipper(self, shippers: List) -> int:
        print("\nСлужбы доставки:")
        for idx, shipper in enumerate(shippers, 1):
            print(f"  {idx}. {shipper.company_name}")

        try:
            shipper_id = int(input("\nВыберите службу доставки (1-3): "))
            if shipper_id not in [1, 2, 3]:
                shipper_id = 1
                print("Выбрана служба доставки по умолчанию")
            return shipper_id
        except ValueError:
            return 1

    def confirm_action(self, message: str) -> bool:
        confirm = input(f"\n{message} (y/n): ").lower()
        return confirm == 'y'

    def get_menu_choice(self, max_option: int) -> str:
        return input("\nВаш выбор: ")

    def ask_continue(self) -> bool:
        another = input("Добавить еще товар? (y/n): ").lower()
        return another == 'y'

    @staticmethod
    def _display_error(message: str):
        print(f"❌ {message}")