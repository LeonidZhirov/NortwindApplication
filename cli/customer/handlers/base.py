# cli/customer/handlers/base.py
from abc import ABC
from typing import Dict, Any
from sqlalchemy.orm import Session

from cli.common.base_handler import BaseHandler
from services import CartService, DisplayService


class BaseCartHandler(BaseHandler, ABC):
    def __init__(self, session: Session):
        super().__init__(session)
        self._cart_service = CartService()
        self._display_service = DisplayService()

    def _display_cart(self, customer_id: str) -> Dict[str, Any]:
        cart_summary = self._cart_service.get_cart_summary(self._session, customer_id)
        if cart_summary['is_empty']:
            print("\n🛒 Корзина пуста")
        else:
            print(self._display_service.format_cart(cart_summary))
        return cart_summary

    def _display_products_simple(self, products, limit: int = 20) -> None:
        print(f"\nДоступные товары (первые {limit}):")
        print("-" * 80)
        for product in products[:limit]:
            print(
                f"ID: {product.product_id:>3} | {product.product_name:<40} | "
                f"Цена: ${float(product.unit_price or 0):>8.2f} | "
                f"Остаток: {product.units_in_stock or 0}"
            )