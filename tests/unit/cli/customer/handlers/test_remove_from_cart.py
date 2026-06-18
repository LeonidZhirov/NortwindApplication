import pytest
from unittest.mock import Mock

from cli.customer.handlers import RemoveFromCartHandler
from models import CartItem


class TestRemoveFromCartHandler:
    @pytest.fixture
    def handler(self, session):
        return RemoveFromCartHandler(session)

    def test_remove_all(self, session, test_customer, test_product, test_cart_item):
        handler = RemoveFromCartHandler(session)

        handler._display_header = Mock()
        handler._wait = Mock()

        handler._input_int = Mock(side_effect=[
            test_product.product_id,
        ])
        handler._input_choice = Mock(return_value=1)

        handler._display_cart = Mock(return_value={
            'is_empty': False,
            'items': [{'product_id': test_product.product_id}]
        })

        handler.handle(customer_id=test_customer.customer_id)

        cart_item = session.query(CartItem).filter(
            CartItem.customer_id == test_customer.customer_id,
            CartItem.product_id == test_product.product_id
        ).first()

        assert cart_item is None
        handler._wait.assert_called_once()

    def test_remove_partial(self, session, test_customer, test_product, test_cart_item):
        handler = RemoveFromCartHandler(session)

        handler._display_header = Mock()
        handler._wait = Mock()
        handler._display_cart = Mock(return_value={
            'is_empty': False,
            'items': [{'product_id': test_product.product_id}]
        })

        handler._input_int = Mock(side_effect=[
            test_product.product_id,
            2,
        ])
        handler._input_choice = Mock(return_value=2)

        handler.handle(customer_id=test_customer.customer_id)

        cart_item = session.query(CartItem).filter(
            CartItem.customer_id == test_customer.customer_id,
            CartItem.product_id == test_product.product_id
        ).first()

        assert cart_item is not None
        assert cart_item.quantity == 3

    def test_remove_cancel(self, session, test_customer, test_product, test_cart_item):
        handler = RemoveFromCartHandler(session)

        handler._display_header = Mock()
        handler._wait = Mock()
        handler._display_cart = Mock(return_value={
            'is_empty': False,
            'items': [{'product_id': test_product.product_id}]
        })

        handler._input_int = Mock(return_value=test_product.product_id)
        handler._input_choice = Mock(return_value=0)

        handler.handle(customer_id=test_customer.customer_id)

        cart_item = session.query(CartItem).filter(
            CartItem.customer_id == test_customer.customer_id,
            CartItem.product_id == test_product.product_id
        ).first()

        assert cart_item is not None
        assert cart_item.quantity == 5

    def test_remove_product_not_in_cart(self, session, test_customer):
        handler = RemoveFromCartHandler(session)

        handler._display_header = Mock()
        handler._wait = Mock()
        handler._display_cart = Mock(return_value={
            'is_empty': False,
            'items': []
        })

        handler._input_int = Mock(return_value=999)

        handler.handle(customer_id=test_customer.customer_id)

        handler._wait.assert_called()