# cli/customer/handlers/cart_handlers.py
from typing import List, Dict, Optional
from sqlalchemy.orm import Session

from cli.customer.handlers.base import BaseCartHandler
from cli.io_utils import parse_id_list
from services import ProductService


class AddToCartHandler(BaseCartHandler):
    def __init__(self, session: Session):
        super().__init__(session)
        self._product_service = ProductService()

    def handle(self, customer_id: str) -> None:
        self._display_header("ДОБАВЛЕНИЕ ТОВАРА")

        products = self._product_service.get_all_products(self._session, limit=20)
        super()._display_products_simple(products)

        while True:
            product_id = self._input_int("\nВведите ID товара (0 для выхода): ", default=0)
            if product_id is None or product_id == 0:
                break

            quantity = self._input_int("Введите количество: ", validator=lambda x: x > 0)
            if quantity is None or quantity <= 0:
                print("❌ Количество должно быть больше 0")
                continue

            success, message, _ = self._cart_service.add_product(
                self._session, customer_id, product_id, quantity
            )

            if success:
                print(f"✅ {message}")
                if not self._confirm("\nДобавить еще товар? (y/n): "):
                    break
            else:
                print(f"❌ {message}")


class ViewCartHandler(BaseCartHandler):
    def handle(self, customer_id: str) -> None:
        self._display_header("КОРЗИНА")
        self._display_cart(customer_id)
        self._wait()


class RemoveFromCartHandler(BaseCartHandler):
    ACTION_CANCEL = 0
    ACTION_REMOVE_ALL = 1
    ACTION_REMOVE_PARTIAL = 2

    def handle(self, customer_id: str) -> None:
        self._display_header("УДАЛЕНИЕ ИЗ КОРЗИНЫ")

        cart_summary = self._display_cart(customer_id)
        if cart_summary['is_empty']:
            self._wait()
            return

        product_id = self._input_int(
            "\nВведите ID товара для удаления (0 для выхода): ",
            default=0
        )
        if product_id is None or product_id == 0:
            return

        cart_item = self._cart_service.get_cart_item(
            self._session, customer_id, product_id
        )

        if not cart_item:
            print("❌ Товар не найден в корзине")
            self._wait()
            return

        self._show_remove_options(cart_item, customer_id)
        self._wait()

    def _show_remove_options(self, cart_item, customer_id: str) -> None:
        print(f"\n📦 Товар: {cart_item.product.product_name}")
        print(f"📊 В корзине: {cart_item.quantity} шт.")
        print("\nВыберите действие:")
        print(f"  {self.ACTION_REMOVE_ALL}. Удалить весь товар")
        print(f"  {self.ACTION_REMOVE_PARTIAL}. Удалить часть (указать количество)")
        print(f"  {self.ACTION_CANCEL}. Отмена")

        action = self._input_choice("\nВаш выбор: ", 2)

        if action == self.ACTION_CANCEL:
            return
        elif action == self.ACTION_REMOVE_ALL:
            self._remove_all(cart_item, customer_id)
        elif action == self.ACTION_REMOVE_PARTIAL:
            self._remove_partial(cart_item, customer_id)

    def _remove_all(self, cart_item, customer_id: str) -> None:
        success, message = self._cart_service.remove_product(
            self._session, customer_id, cart_item.product_id
        )
        print(f"{'✅' if success else '❌'} {message}")

    def _remove_partial(self, cart_item, customer_id: str) -> None:
        max_qty = cart_item.quantity

        quantity = self._input_int(
            f"Введите количество для удаления (1-{max_qty}): ",
            validator=lambda x: 1 <= x <= max_qty
        )

        if quantity is None:
            return

        success, message = self._cart_service.remove_product(
            self._session, customer_id, cart_item.product_id, quantity
        )
        print(f"{'✅' if success else '❌'} {message}")


class BatchRemoveFromCartHandler(BaseCartHandler):
    def handle(self, customer_id: str) -> None:
        self._display_header("МАССОВОЕ УДАЛЕНИЕ ИЗ КОРЗИНЫ")

        cart_summary = self._display_cart(customer_id)
        if cart_summary['is_empty']:
            self._wait()
            return

        product_ids = self._get_product_ids_to_remove(cart_summary['items'])
        if not product_ids:
            return

        self._confirm_and_remove(customer_id, cart_summary['items'], product_ids)
        self._wait()

    def _get_product_ids_to_remove(self, cart_items: List[Dict]) -> Optional[List[int]]:
        print("\n💡 Введите ID товаров для удаления через запятую")
        print("   Например: 1, 3, 5")
        print("   Или: 1-5 (диапазон)")
        print("   0 - отмена")

        user_input = input("\n👉 Ваш выбор: ").strip()

        if user_input == '0':
            return None

        valid_ids = {item['product_id'] for item in cart_items}
        product_ids = parse_id_list(user_input, valid_ids)

        if not product_ids:
            print("❌ Не найдено товаров для удаления")
            return None

        return product_ids

    def _confirm_and_remove(
            self,
            customer_id: str,
            cart_items: List[Dict],
            product_ids: List[int]
    ) -> None:
        self._show_products_to_remove(cart_items, product_ids)

        if not self._confirm("\nПодтвердить удаление? (y/n): "):
            print("❌ Удаление отменено")
            return

        removed_count = self._remove_products(customer_id, product_ids)
        print(f"\n✅ Удалено {removed_count} товаров из корзины")

    def _show_products_to_remove(self, cart_items: List[Dict], product_ids: List[int]) -> None:
        print(f"\n📋 Будет удалено {len(product_ids)} товаров:")
        for item in cart_items:
            if item['product_id'] in product_ids:
                print(f"  - {item['product_name']} ({item['quantity']} шт.)")

    def _remove_products(self, customer_id: str, product_ids: List[int]) -> int:
        removed_count = 0

        for product_id in product_ids:
            success, message = self._cart_service.remove_product(
                self._session, customer_id, product_id
            )

            if success:
                removed_count += 1
                print(f"✅ {message}")
            else:
                print(f"❌ {message}")

        return removed_count