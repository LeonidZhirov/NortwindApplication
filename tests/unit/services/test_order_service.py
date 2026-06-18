# tests/services/test_order_service.py
import pytest
from datetime import date
from decimal import Decimal

from services.order_service import OrderService
from services.stock_manager import InsufficientStockError
from models.order_model import Order
from models.order_detail_model import OrderDetail


class TestOrderService:
    @pytest.fixture
    def order_service(self):
        return OrderService()

    @pytest.fixture
    def cart_items(self, test_product):
        return [
            {
                'product_id': test_product.product_id,
                'quantity': 2,
                'unit_price': 10.0
            }
        ]


    def test_create_order_from_cart_success(
            self, session, test_customer, test_product, cart_items, order_service
    ):
        assert test_product.units_in_stock == 100

        order = order_service.create_order_from_cart(
            session=session,
            customer_id=test_customer.customer_id,
            cart_items=cart_items,
            employee_id=1,
            shipper_id=1
        )

        assert order is not None
        assert order.order_id is not None
        assert order.customer_id == test_customer.customer_id
        assert order.order_date == date.today()

        assert len(order.details) == 1
        assert order.details[0].product_id == test_product.product_id
        assert order.details[0].quantity == 2
        assert order.details[0].unit_price == 10.0

        session.refresh(test_product)

        assert test_product.units_in_stock == 100

        order_service.ship_order(session, order.order_id)
        session.refresh(test_product)
        assert test_product.units_in_stock == 98

    def test_create_order_from_cart_insufficient_stock(
            self, session, test_customer, test_product, order_service
    ):
        test_product.units_in_stock = 1
        session.flush()

        cart_items = [
            {
                'product_id': test_product.product_id,
                'quantity': 5,
                'unit_price': 10.0
            }
        ]

        with pytest.raises(InsufficientStockError) as exc_info:
            order_service.create_order_from_cart(
                session=session,
                customer_id=test_customer.customer_id,
                cart_items=cart_items,
                employee_id=1,
                shipper_id=1
            )

        assert "Недостаточно" in str(exc_info.value)
        assert test_product.product_name in str(exc_info.value)

        session.refresh(test_product)
        assert test_product.units_in_stock == 1

    def test_create_order_from_cart_product_not_found(
        self, session, test_customer, order_service
    ):
        cart_items = [
            {
                'product_id': 999,
                'quantity': 2,
                'unit_price': 10.0
            }
        ]

        with pytest.raises(ValueError) as exc_info:
            order_service.create_order_from_cart(
                session=session,
                customer_id=test_customer.customer_id,
                cart_items=cart_items,
                employee_id=1,
                shipper_id=1
            )

        assert "не найден" in str(exc_info.value)

    def test_get_customer_orders(self, session, test_customer, test_product, order_service):
        for i in range(3):
            order = Order(
                customer_id=test_customer.customer_id,
                employee_id=1,
                order_date=date.today()
            )
            session.add(order)
            session.flush()

            detail = OrderDetail(
                order_id=order.order_id,
                product_id=test_product.product_id,
                quantity=1,
                unit_price=10.0,
                discount=0
            )
            session.add(detail)
            session.flush()

        orders = order_service.get_customer_orders(session, test_customer.customer_id)
        assert len(orders) == 3

    def test_get_order_summary(self, session, test_customer, test_product, order_service):
        order = Order(
            customer_id=test_customer.customer_id,
            employee_id=1,
            order_date=date.today()
        )
        session.add(order)
        session.flush()

        detail = OrderDetail(
            order_id=order.order_id,
            product_id=test_product.product_id,
            quantity=3,
            unit_price=10.0,
            discount=0
        )
        session.add(detail)
        session.flush()

        summary = order_service.get_order_summary(session, order.order_id)

        assert summary is not None
        assert summary['order_id'] == order.order_id
        assert summary['customer_id'] == test_customer.customer_id
        assert summary['items_count'] == 1
        assert summary['total_quantity'] == 3
        assert summary['total'] == Decimal('30.00')

    def test_get_order_summary_not_found(self, session, order_service):
        summary = order_service.get_order_summary(session, 999)
        assert summary is None

    def test_cancel_order_success(self, session, test_customer, test_product, order_service):
        test_product.units_in_stock = 100
        session.flush()

        cart_items = [
            {
                'product_id': test_product.product_id,
                'quantity': 3,
                'unit_price': 10.0
            }
        ]

        order = order_service.create_order_from_cart(
            session=session,
            customer_id=test_customer.customer_id,
            cart_items=cart_items,
            employee_id=1,
            shipper_id=1
        )

        session.refresh(test_product)
        assert test_product.units_in_stock == 100

        result = order_service.cancel_order(session, order.order_id)
        assert result is True

        session.refresh(test_product)
        assert test_product.units_in_stock == 100  # Остаток не изменился

        deleted_order = session.query(Order).filter(
            Order.order_id == order.order_id
        ).first()
        assert deleted_order is None

    def test_cancel_order_not_found(self, session, order_service):
        with pytest.raises(ValueError) as exc_info:
            order_service.cancel_order(session, 999)

        assert "не найден" in str(exc_info.value)

    def test_cancel_order_already_shipped(self, session, test_customer, test_product, order_service):
        test_product.units_in_stock = 100
        session.flush()

        cart_items = [
            {
                'product_id': test_product.product_id,
                'quantity': 2,
                'unit_price': 10.0
            }
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
        assert test_product.units_in_stock == 98

        with pytest.raises(ValueError) as exc_info:
            order_service.cancel_order(session, order.order_id)

        assert "отгруженный" in str(exc_info.value)

        session.refresh(test_product)
        assert test_product.units_in_stock == 98

        existing_order = session.query(Order).filter(
            Order.order_id == order.order_id
        ).first()
        assert existing_order is not None
        assert existing_order.is_shipped is True