# tests/services/test_cart_service.py
import pytest
from decimal import Decimal

from services.cart_service import CartService


class TestCartService:
    @pytest.fixture
    def cart_service(self):
        return CartService()

    def test_add_product_success(self, session, test_customer, test_product, cart_service):
        result = cart_service.add_product(
            session,
            customer_id=test_customer.customer_id,
            product_id=test_product.product_id,
            quantity=2
        )

        assert result.success is True
        assert result.cart_item is not None
        assert result.cart_item.quantity == 2
        assert "Добавлено" in result.message

    def test_add_product_not_found(self, session, test_customer, cart_service):
        result = cart_service.add_product(
            session,
            customer_id=test_customer.customer_id,
            product_id=999,
            quantity=2
        )

        assert result.success is False
        assert result.cart_item is None
        assert "Товар не найден" in result.message

    def test_add_product_discontinued(self, session, test_customer, test_product, cart_service):
        test_product.discontinued = 1
        session.flush()

        result = cart_service.add_product(
            session,
            customer_id=test_customer.customer_id,
            product_id=test_product.product_id,
            quantity=2
        )

        assert result.success is False
        assert "снят с производства" in result.message

    def test_add_product_insufficient_stock(self, session, test_customer, test_product, cart_service):
        test_product.units_in_stock = 1
        session.flush()

        result = cart_service.add_product(
            session,
            customer_id=test_customer.customer_id,
            product_id=test_product.product_id,
            quantity=5
        )

        assert result.success is False
        assert "Недостаточно" in result.message

    def test_remove_product_success(self, session, test_customer, test_product, test_cart_item, cart_service):
        success, message = cart_service.remove_product(
            session,
            customer_id=test_customer.customer_id,
            product_id=test_product.product_id
        )

        assert success is True
        assert "удален" in message

        cart = cart_service.get_cart(session, test_customer.customer_id)
        assert len(cart) == 0

    def test_remove_product_not_in_cart(self, session, test_customer, cart_service):
        success, message = cart_service.remove_product(
            session,
            customer_id=test_customer.customer_id,
            product_id=999
        )

        assert success is False
        assert "не найден" in message

    def test_get_cart_summary(self, session, test_customer, test_product, test_cart_item, cart_service):
        summary = cart_service.get_cart_summary(session, test_customer.customer_id)

        assert summary['is_empty'] is False
        assert summary['items_count'] == 1
        assert summary['total_quantity'] == 5
        assert summary['total'] == Decimal('50.00')

    def test_clear_cart(self, session, test_customer, test_cart_item, cart_service):
        count = cart_service.clear_cart(session, test_customer.customer_id)
        assert count == 1

        cart = cart_service.get_cart(session, test_customer.customer_id)
        assert len(cart) == 0