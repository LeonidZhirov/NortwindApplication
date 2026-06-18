# cli/customer/handlers/product_handlers.py
from typing import Optional
from sqlalchemy.orm import Session

from cli.common.base_handler import BaseHandler
from services import ProductService, CartService, DisplayService


class ShowProductsHandler(BaseHandler):
    def __init__(self, session: Session):
        super().__init__(session)
        self._product_service = ProductService()
        self._cart_service = CartService()
        self._display_service = DisplayService()

    def handle(self, customer_id: Optional[str] = None) -> None:
        self._display_header("КАТАЛОГ ТОВАРОВ")

        products = self._product_service.get_all_products(self._session)
        if not products:
            print("Товары не найдены")
            self._wait()
            return

        cart_product_ids = []
        if customer_id:
            cart = self._cart_service.get_cart(self._session, customer_id)
            cart_product_ids = [item.product_id for item in cart]

        print(self._display_service.format_products(products, cart_product_ids))
        self._wait()