# cli/customer/role.py
from typing import Dict, Callable, Optional

from cli.base_role import BaseRole
from cli.common.session_manager import SessionManager
from cli.customer.handlers import (
    ShowProductsHandler,
    AddToCartHandler,
    ViewCartHandler,
    RemoveFromCartHandler,
    CheckoutHandler,
    SelectCustomerHandler,
    ShowOrdersHandler,
    BatchRemoveFromCartHandler
)
from services import CartService, DisplayService


class CustomerRole(BaseRole):
    def __init__(self, cli_context):
        super().__init__(cli_context)
        self._customer_id: Optional[str] = None
        self._session_manager = SessionManager()
        self._display_service = DisplayService()
        self._cart_service = CartService()
        self._initialized = False

    def _setup_services(self) -> None:
        pass

    def get_role_name(self) -> str:
        return "РЕЖИМ ПОКУПАТЕЛЯ 👤"

    def get_status_info(self) -> Optional[str]:
        if not self._customer_id:
            return "⚠️ Клиент не выбран. Выберите клиента (пункт 5)"

        with self._session_manager.session() as session:
            cart_summary = self._cart_service.get_cart_summary(session, self._customer_id)
            return (
                f"👤 Клиент ID: {self._customer_id}\n"
                f"🛒 Корзина: {cart_summary['items_count']} позиций, "
                f"{cart_summary['total_quantity']} шт., "
                f"сумма: ${float(cart_summary['total']):.2f}"
            )

    def get_menu_items(self) -> Dict[str, tuple[str, Callable]]:
        return {
            '1': ("📋 Просмотреть каталог товаров", self._show_products),
            '2': ("➕ Добавить товар в корзину", self._add_to_cart),
            '3': ("🛒 Посмотреть корзину", self._view_cart),
            '4': ("💳 Оформить заказ", self._checkout),
            '5': ("🔄 Сменить клиента", self._select_customer),
            '6': ("❌ Удалить товар из корзины", self._remove_from_cart),
            '7': ("🗑️ Массовое удаление из корзины", self._batch_remove_from_cart),  # ← Новый пункт
            '8': ("📝 История моих заказов", self._show_orders),
        }

    def _select_customer_interactive(self) -> bool:
        with self._session_manager.session() as session:
            handler = SelectCustomerHandler(session)
            result = handler.handle()
            if result:
                self._customer_id = result
                return True
            return False

    def _require_customer(self) -> bool:
        if not self._customer_id:
            print("\n❌ Сначала выберите клиента (пункт 5)")
            self._wait()
            return False
        return True

    def _with_session(self, handler_class, *args, **kwargs):
        def wrapper():
            with self._session_manager.session() as session:
                handler = handler_class(session)
                handler.handle(*args, **kwargs)

        return wrapper

    def _show_products(self) -> None:
        self._with_session(ShowProductsHandler, self._customer_id)()

    def _add_to_cart(self) -> None:
        if not self._require_customer():
            return
        self._with_session(AddToCartHandler, self._customer_id)()

    def _view_cart(self) -> None:
        if not self._require_customer():
            return
        self._with_session(ViewCartHandler, self._customer_id)()

    def _remove_from_cart(self) -> None:
        if not self._require_customer():
            return
        self._with_session(RemoveFromCartHandler, self._customer_id)()

    def _checkout(self) -> None:
        if not self._require_customer():
            return
        self._with_session(CheckoutHandler, self._customer_id)()

    def _select_customer(self) -> None:
        self._select_customer_interactive()

    def _show_orders(self) -> None:
        if not self._require_customer():
            return
        self._with_session(ShowOrdersHandler, self._customer_id)()

    def _batch_remove_from_cart(self) -> None:
        if not self._require_customer():
            return
        self._with_session(BatchRemoveFromCartHandler, self._customer_id)()

    def run(self) -> None:
        if not hasattr(self, '_welcomed'):
            print("\n👋 Добро пожаловать в режим покупателя!")
            print("Для начала работы необходимо выбрать клиента.\n")
            self._welcomed = True

        if not self._customer_id:
            if not self._select_customer_interactive():
                print("\n❌ Клиент не выбран. Возврат в главное меню.")
                self._wait()
                return

        super().run()