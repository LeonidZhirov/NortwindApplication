# tests/integration/executor/test_shipping_scenarios.py
import pytest
from datetime import date

from services import OrderService, StockService

class TestShippingScenarios:
    def test_ship_order_with_sufficient_stock(self, session, test_customer, test_product):
        order_service = OrderService()
        stock_service = StockService()

        test_product.units_in_stock = 20
        session.flush()

        cart_items = [
            {'product_id': test_product.product_id, 'quantity': 3, 'unit_price': 10.0}
        ]
        order = order_service.create_order_from_cart(
            session=session,
            customer_id=test_customer.customer_id,
            cart_items=cart_items,
            employee_id=1,
            shipper_id=1
        )

        session.refresh(test_product)
        assert test_product.units_in_stock == 20

        shipped_order = order_service.ship_order(session, order.order_id)

        session.refresh(test_product)
        assert test_product.units_in_stock == 17

        assert shipped_order.shipped_date == date.today()
        assert shipped_order.is_shipped is True

        alerts = stock_service.get_pending_alerts(session)
        alerts_for_product = [a for a in alerts if a.product_id == test_product.product_id]
        assert len(alerts_for_product) == 0

    def test_ship_order_creates_alert_on_low_stock(self, session, test_customer, test_product):
        order_service = OrderService()
        stock_service = StockService()

        test_product.units_in_stock = 10
        test_product.reorder_level = 10
        session.flush()

        cart_items = [
            {'product_id': test_product.product_id, 'quantity': 3, 'unit_price': 10.0}
        ]
        order = order_service.create_order_from_cart(
            session=session,
            customer_id=test_customer.customer_id,
            cart_items=cart_items,
            employee_id=1,
            shipper_id=1
        )

        order_service.ship_order(session, order.order_id)

        session.refresh(test_product)
        assert test_product.units_in_stock == 7

        alerts = stock_service.get_pending_alerts(session)
        alerts_for_product = [a for a in alerts if a.product_id == test_product.product_id]
        assert len(alerts_for_product) == 1
        assert alerts_for_product[0].current_stock == 7
        assert alerts_for_product[0].reorder_level == 10

    def test_ship_order_stock_becomes_insufficient(self, session, test_customer, test_product):
        order_service = OrderService()

        test_product.units_in_stock = 10
        session.flush()

        cart_items = [
            {'product_id': test_product.product_id, 'quantity': 5, 'unit_price': 10.0}
        ]
        order = order_service.create_order_from_cart(
            session=session,
            customer_id=test_customer.customer_id,
            cart_items=cart_items,
            employee_id=1,
            shipper_id=1
        )

        test_product.units_in_stock = 3
        session.flush()

        with pytest.raises(ValueError) as exc_info:
            order_service.ship_order(session, order.order_id)

        error_msg = str(exc_info.value)
        assert "product_id" in error_msg
        assert str(test_product.product_id) in error_msg
        assert "available': 3" in error_msg
        assert "shortage': 2" in error_msg

        session.refresh(test_product)
        assert test_product.units_in_stock == 3

    def test_ship_multiple_orders_sequential(self, session, test_customer, test_product):
        order_service = OrderService()

        test_product.units_in_stock = 20
        session.flush()

        orders = []
        for i in range(3):
            cart_items = [
                {'product_id': test_product.product_id, 'quantity': 2, 'unit_price': 10.0}
            ]
            order = order_service.create_order_from_cart(
                session=session,
                customer_id=test_customer.customer_id,
                cart_items=cart_items,
                employee_id=1,
                shipper_id=1
            )
            orders.append(order)
            session.refresh(test_product)
            assert test_product.units_in_stock == 20

        for i, order in enumerate(orders, 1):
            order_service.ship_order(session, order.order_id)
            session.refresh(test_product)
            expected_stock = 20 - (i * 2)
            assert test_product.units_in_stock == expected_stock

    def test_ship_order_employee_assignment(self, session, test_customer, test_product):
        """Проверка назначения сотрудника при отгрузке."""
        order_service = OrderService()

        test_product.units_in_stock = 10
        session.flush()

        cart_items = [
            {'product_id': test_product.product_id, 'quantity': 2, 'unit_price': 10.0}
        ]
        order = order_service.create_order_from_cart(
            session=session,
            customer_id=test_customer.customer_id,
            cart_items=cart_items,
            employee_id=1,
            shipper_id=1
        )

        # Отгружаем с сотрудником 2
        shipped_order = order_service.ship_order(session, order.order_id, employee_id=2)
        assert shipped_order.employee_id == 2