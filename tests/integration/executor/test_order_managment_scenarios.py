# tests/integration/executor/test_order_management_scenarios.py
from services import OrderService, StockService
from models import  Product


class TestOrderManagementScenarios:
    def test_view_unshipped_orders(self, session, test_customer, test_product):
        order_service = OrderService()

        for i in range(3):
            cart_items = [
                {'product_id': test_product.product_id, 'quantity': 1, 'unit_price': 10.0}
            ]
            order_service.create_order_from_cart(
                session=session,
                customer_id=test_customer.customer_id,
                cart_items=cart_items,
                employee_id=1,
                shipper_id=1
            )

        unshipped = order_service.get_unshipped_orders(session)
        assert len(unshipped) == 3

        order_service.ship_order(session, unshipped[0].order_id)

        unshipped = order_service.get_unshipped_orders(session)
        assert len(unshipped) == 2

    def test_view_shipped_history(self, session, test_customer, test_product):
        order_service = OrderService()

        for i in range(3):
            cart_items = [
                {'product_id': test_product.product_id, 'quantity': 1, 'unit_price': 10.0}
            ]
            order = order_service.create_order_from_cart(
                session=session,
                customer_id=test_customer.customer_id,
                cart_items=cart_items,
                employee_id=1,
                shipper_id=1
            )
            order_service.ship_order(session, order.order_id)

        shipped = order_service.get_shipped_orders(session, limit=10)
        assert len(shipped) == 3

        dates = [o.shipped_date for o in shipped]
        assert dates == sorted(dates, reverse=True)

    def test_view_order_details(self, session, test_customer, test_product):
        order_service = OrderService()

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

        summary = order_service.get_order_summary(session, order.order_id)
        assert summary is not None
        assert summary['order_id'] == order.order_id
        assert summary['items_count'] == 1
        assert summary['total_quantity'] == 3
        assert summary['total'] == 30.0

    def test_order_statistics(self, session, test_customer, test_product):
        order_service = OrderService()

        test_product.units_in_stock = 100
        session.flush()

        for i in range(5):
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
            if i < 3:
                order_service.ship_order(session, order.order_id)

        stats = order_service.get_statistics(session)
        assert stats['total_orders'] == 5
        assert stats['shipped_orders'] == 3
        assert stats['unshipped_orders'] == 2
        assert stats['total_amount'] > 0
        assert stats['average_amount'] > 0

    def test_order_validation_before_shipment(self, session, test_customer, test_product):
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

        can_ship, issues = order_service.validate_order_shippable(
            session, order.order_id
        )
        assert can_ship is True
        assert len(issues) == 0

        test_product.units_in_stock = 2
        session.flush()

        can_ship, issues = order_service.validate_order_shippable(
            session, order.order_id
        )
        assert can_ship is False
        assert len(issues) == 1
        assert issues[0]['shortage'] == 3

    def test_ship_order_with_multiple_products(self, session, test_customer):
        order_service = OrderService()

        products = []
        for i in range(3):
            product = Product(
                product_name=f"Test Product {i+1}",
                unit_price=10.0 + i,
                units_in_stock=20,
                reorder_level=5,
                supplier_id=1,
                discontinued=0
            )
            session.add(product)
            session.flush()
            products.append(product)

        cart_items = [
            {'product_id': products[0].product_id, 'quantity': 3, 'unit_price': 10.0},
            {'product_id': products[1].product_id, 'quantity': 2, 'unit_price': 12.0},
            {'product_id': products[2].product_id, 'quantity': 1, 'unit_price': 14.0},
        ]
        order = order_service.create_order_from_cart(
            session=session,
            customer_id=test_customer.customer_id,
            cart_items=cart_items,
            employee_id=1,
            shipper_id=1
        )

        order_service.ship_order(session, order.order_id)

        for i, product in enumerate(products):
            session.refresh(product)
            expected_stock = 20 - cart_items[i]['quantity']
            assert product.units_in_stock == expected_stock