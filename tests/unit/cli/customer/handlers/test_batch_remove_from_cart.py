import pytest
from unittest.mock import Mock, patch

from cli.customer.handlers import BatchRemoveFromCartHandler


class TestBatchRemoveFromCartHandler:
    @pytest.fixture
    def handler(self, session):
        return BatchRemoveFromCartHandler(session)

    @pytest.fixture
    def multiple_cart_items(self, session, test_customer):
        from models.product_model import Product
        from models.cart_item_model import CartItem

        products = []
        for i in range(3):
            product = Product(
                product_name=f"Test Product {i + 1}",
                unit_price=10.0 + i,
                units_in_stock=100,
                discontinued=0
            )
            session.add(product)
            session.flush()
            products.append(product)

            cart_item = CartItem(
                customer_id=test_customer.customer_id,
                product_id=product.product_id,
                product_name=product.product_name,
                quantity=(i + 1) * 2,
                unit_price=10.0 + i
            )
            session.add(cart_item)
            session.flush()

        return products

    @patch('builtins.input')
    def test_remove_multiple(self, mock_input, session, test_customer, multiple_cart_items):
        handler = BatchRemoveFromCartHandler(session)
        handler._display_header = lambda x: None
        handler._wait = Mock()
        handler._display_cart = lambda x: {
            'is_empty': False,
            'items': [
                {'product_id': item.product_id, 'product_name': item.product_name, 'quantity': (i + 1) * 2}
                for i, item in enumerate(multiple_cart_items)
            ]
        }
        handler._confirm = Mock(return_value=True)

        mock_input.side_effect = [
            f"{multiple_cart_items[0].product_id}, {multiple_cart_items[2].product_id}",
            "y"
        ]

        handler.handle(customer_id=test_customer.customer_id)

        from models.cart_item_model import CartItem
        remaining = session.query(CartItem).filter(
            CartItem.customer_id == test_customer.customer_id
        ).all()

        assert len(remaining) == 1
        assert remaining[0].product_id == multiple_cart_items[1].product_id
        handler._wait.assert_called()

    @patch('builtins.input')
    def test_remove_range(self, mock_input, session, test_customer, multiple_cart_items):
        handler = BatchRemoveFromCartHandler(session)
        handler._display_header = lambda x: None
        handler._wait = Mock()
        handler._display_cart = lambda x: {
            'is_empty': False,
            'items': [
                {'product_id': item.product_id, 'product_name': item.product_name, 'quantity': (i + 1) * 2}
                for i, item in enumerate(multiple_cart_items)
            ]
        }
        handler._confirm = Mock(return_value=True)

        mock_input.side_effect = [
            "1-2",
            "y"
        ]

        handler.handle(customer_id=test_customer.customer_id)

        from models.cart_item_model import CartItem
        remaining = session.query(CartItem).filter(
            CartItem.customer_id == test_customer.customer_id
        ).all()

        assert len(remaining) == 1
        assert remaining[0].product_id == multiple_cart_items[2].product_id
        handler._wait.assert_called()

    @patch('builtins.input')
    def test_remove_cancel(self, mock_input, session, test_customer, multiple_cart_items):
        handler = BatchRemoveFromCartHandler(session)
        handler._display_header = lambda x: None
        handler._wait = Mock()
        handler._display_cart = lambda x: {
            'is_empty': False,
            'items': [
                {'product_id': item.product_id, 'product_name': item.product_name, 'quantity': (i + 1) * 2}
                for i, item in enumerate(multiple_cart_items)
            ]
        }

        mock_input.side_effect = ["0"]

        handler.handle(customer_id=test_customer.customer_id)

        from models.cart_item_model import CartItem
        remaining = session.query(CartItem).filter(
            CartItem.customer_id == test_customer.customer_id
        ).count()

        assert remaining == 3
        handler._wait.assert_not_called()

    @patch('builtins.input')
    def test_remove_invalid_input(self, mock_input, session, test_customer, multiple_cart_items):
        handler = BatchRemoveFromCartHandler(session)
        handler._display_header = lambda x: None
        handler._wait = Mock()
        handler._display_cart = lambda x: {
            'is_empty': False,
            'items': [
                {'product_id': item.product_id, 'product_name': item.product_name, 'quantity': (i + 1) * 2}
                for i, item in enumerate(multiple_cart_items)
            ]
        }

        mock_input.side_effect = [
            "invalid",
            "0"
        ]

        handler.handle(customer_id=test_customer.customer_id)

        from models.cart_item_model import CartItem
        remaining = session.query(CartItem).filter(
            CartItem.customer_id == test_customer.customer_id
        ).count()

        assert remaining == 3