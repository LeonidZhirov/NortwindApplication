import pytest
from unittest.mock import Mock

from cli.customer.handlers import ShowProductsHandler
from models import CartItem


class TestShowProductsHandler:
    @pytest.fixture
    def handler(self, session):
        return ShowProductsHandler(session)

    def test_handle_with_customer(self, session, test_customer, test_product):
        handler = ShowProductsHandler(session)

        handler._wait = Mock()
        handler._display_header = Mock()

        cart_item = CartItem(
            customer_id=test_customer.customer_id,
            product_id=test_product.product_id,
            product_name=test_product.product_name,
            quantity=2,
            unit_price=10.0
        )
        session.add(cart_item)
        session.flush()

        handler.handle(customer_id=test_customer.customer_id)

        handler._wait.assert_called_once()
        handler._display_header.assert_called_once()

    def test_handle_no_products(self, session):
        handler = ShowProductsHandler(session)

        handler._wait = Mock()
        handler._display_header = Mock()

        from models.product_model import Product
        session.query(Product).delete()
        session.flush()

        handler.handle()

        handler._wait.assert_called_once()
        handler._display_header.assert_called_once()