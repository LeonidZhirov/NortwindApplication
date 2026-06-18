import pytest

from services import CartService, OrderService


class TestOrderScenarios:
    def test_cancel_order_before_shipping(self, session, test_customer, test_product):
        cart_service = CartService()
        order_service = OrderService()

        cart_service.add_product(
            session=session,
            customer_id=test_customer.customer_id,
            product_id=test_product.product_id,
            quantity=3
        )

        order = order_service.create_order_from_cart(
            session=session,
            customer_id=test_customer.customer_id,
            cart_items=[{'product_id': test_product.product_id, 'quantity': 3, 'unit_price': 10.0}],
            employee_id=1,
            shipper_id=1
        )

        cart_service.clear_cart(session, test_customer.customer_id)
        session.refresh(test_product)
        assert test_product.units_in_stock == 100

        # Отмена
        result = order_service.cancel_order(session, order.order_id)
        assert result is True

        orders = order_service.get_customer_orders(session, test_customer.customer_id)
        assert len(orders) == 0
        session.refresh(test_product)
        assert test_product.units_in_stock == 100

    def test_cancel_shipped_order_fails(self, session, test_customer, test_product):
        """Попытка отмены отгруженного заказа."""
        cart_service = CartService()
        order_service = OrderService()

        cart_service.add_product(
            session=session,
            customer_id=test_customer.customer_id,
            product_id=test_product.product_id,
            quantity=3
        )

        order = order_service.create_order_from_cart(
            session=session,
            customer_id=test_customer.customer_id,
            cart_items=[{'product_id': test_product.product_id, 'quantity': 3, 'unit_price': 10.0}],
            employee_id=1,
            shipper_id=1
        )

        cart_service.clear_cart(session, test_customer.customer_id)

        order_service.ship_order(session, order.order_id)
        session.refresh(test_product)
        assert test_product.units_in_stock == 97

        with pytest.raises(ValueError) as exc_info:
            order_service.cancel_order(session, order.order_id)

        assert "отгруженный" in str(exc_info.value)
        session.refresh(test_product)
        assert test_product.units_in_stock == 97