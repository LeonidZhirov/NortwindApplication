# cli/customer/handlers/order_handlers.py
from typing import Dict
from sqlalchemy.orm import Session

from cli.customer.handlers.base import BaseCartHandler
from services import OrderService
from repositories import ShipperRepository

from sqlalchemy.orm import Session

from cli.common.base_handler import BaseHandler
from services import OrderService, DisplayService


class ShowOrdersHandler(BaseHandler):
    def __init__(self, session: Session):
        super().__init__(session)
        self._order_service = OrderService()
        self._display_service = DisplayService()

    def handle(self, customer_id: str) -> None:
        orders = self._order_service.get_customer_orders(self._session, customer_id)

        if not orders:
            print("\n📭 У вас пока нет заказов")
        else:
            print(self._display_service.format_orders(orders, with_status=True))

        self._wait()


class CheckoutHandler(BaseCartHandler):
    def __init__(self, session: Session):
        super().__init__(session)
        self._order_service = OrderService()

    def handle(self, customer_id: str) -> None:
        self._display_header("ОФОРМЛЕНИЕ ЗАКАЗА")

        cart_summary = self._display_cart(customer_id)
        if cart_summary['is_empty']:
            self._wait()
            return

        if not self._validate_stock(customer_id):
            return

        shipper_id = self._select_shipper()
        if shipper_id is None:
            return

        self._show_order_details(cart_summary)
        if not self._confirm("\nПодтвердить заказ? (y/n): "):
            print("❌ Заказ отменен")
            self._wait()
            return

        order = self._create_order(customer_id, cart_summary, shipper_id)

        self._cart_service.clear_cart(self._session, customer_id)

        self._show_success(order, cart_summary)
        self._wait()

    def _validate_stock(self, customer_id: str) -> bool:
        has_stock, issues = self._cart_service.validate_cart_stock(
            self._session, customer_id
        )

        if has_stock:
            return True

        print("\n❌ Невозможно оформить заказ из-за нехватки товаров:")
        for issue in issues:
            print(
                f"  - {issue['product_name']}: нужно {issue['required']}, "
                f"есть {issue['available']}"
            )
        self._wait()
        return False

    def _select_shipper(self) -> int:
        shippers = self._order_service.get_shippers(self._session)

        if not shippers:
            print("⚠️ Службы доставки не найдены. Используется ID: 1")
            return 1

        print("\nСлужбы доставки:")
        for shipper in shippers:
            print(f"  {shipper.shipper_id}. {shipper.company_name}")

        default_shipper = self._order_service.get_default_shipper(self._session)
        default_id = default_shipper.shipper_id if default_shipper else 1

        choice = self._input_int(
            f"\nВыберите службу доставки (по умолчанию: {default_id}): ",
            default=default_id
        )

        shipper_ids = {s.shipper_id for s in shippers}
        if choice is None or choice not in shipper_ids:
            print(f"Выбрана служба доставки по умолчанию (ID: {default_id})")
            return default_id

        return choice

    def _show_order_details(self, cart_summary: Dict) -> None:
        print("\n📋 Детали заказа:")
        print(f"  Сумма: ${float(cart_summary['total']):.2f}")
        print(f"  Всего позиций: {cart_summary['items_count']}")
        print(f"  Всего шт.: {cart_summary['total_quantity']}")

    def _create_order(self, customer_id: str, cart_summary: Dict, shipper_id: int):
        order_items = [
            {
                'product_id': item['product_id'],
                'quantity': item['quantity'],
                'unit_price': item['unit_price']
            }
            for item in cart_summary['items']
        ]

        return self._order_service.create_order_from_cart(
            session=self._session,
            customer_id=customer_id,
            cart_items=order_items,
            shipper_id=shipper_id
        )

    def _show_success(self, order, cart_summary: Dict) -> None:
        print("\n" + "=" * 80)
        print(" 🎉 ЗАКАЗ УСПЕШНО СОЗДАН! 🎉 ".center(80, "="))
        print("=" * 80)
        print(f"\n  Номер заказа: #{order.order_id}")
        print(f"  Дата заказа: {order.order_date}")
        print(f"  Сумма заказа: ${float(cart_summary['total']):.2f}")
        print(f"\n  Спасибо за покупку! 🛍️")