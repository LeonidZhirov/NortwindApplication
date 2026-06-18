import pytest
from unittest.mock import Mock

from cli.customer.handlers import AddToCartHandler
from models import CartItem


class TestAddToCartHandler:
    @pytest.fixture
    def handler(self, session):
        return AddToCartHandler(session)

    def test_add_to_cart_success(self, session, test_customer, test_product):
        handler = AddToCartHandler(session)

        handler._display_header = Mock()
        handler._wait = Mock()
        handler._display_products = Mock()

        handler._input_int = Mock(side_effect=[
            test_product.product_id,
            2,
        ])
        handler._confirm = Mock(return_value=False)

        handler.handle(customer_id=test_customer.customer_id)

        cart_item = session.query(CartItem).filter(
            CartItem.customer_id == test_customer.customer_id,
            CartItem.product_id == test_product.product_id
        ).first()

        assert cart_item is not None
        assert cart_item.quantity == 2
        handler._display_header.assert_called_once()

    def test_add_to_cart_cancel(self, session, test_customer):
        handler = AddToCartHandler(session)

        handler._display_header = Mock()
        handler._wait = Mock()
        handler._display_products = Mock()

        handler._input_int = Mock(return_value=0)

        handler.handle(customer_id=test_customer.customer_id)

        cart_items = session.query(CartItem).filter(
            CartItem.customer_id == test_customer.customer_id
        ).all()
        assert len(cart_items) == 0
        handler._wait.assert_not_called()

    def test_add_to_cart_insufficient_stock(self, session, test_customer, test_product):
        test_product.units_in_stock = 1
        session.flush()

        handler = AddToCartHandler(session)

        handler._display_header = Mock()
        handler._wait = Mock()
        handler._display_products = Mock()

        handler._input_int = Mock(side_effect=[
            test_product.product_id,
            5,
            0,
        ])
        handler._confirm = Mock(return_value=False)

        handler.handle(customer_id=test_customer.customer_id)

        cart_item = session.query(CartItem).filter(
            CartItem.customer_id == test_customer.customer_id,
            CartItem.product_id == test_product.product_id
        ).first()

        assert cart_item is None
        handler._display_header.assert_called_once()