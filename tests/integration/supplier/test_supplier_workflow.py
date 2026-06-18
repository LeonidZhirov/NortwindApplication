# tests/integration/supplier/test_supplier_workflow.py
from services import StockService, ProductService


class TestSupplierWorkflow:
    def test_full_supplier_workflow(self, session, test_customer, test_product, test_supplier):
        from services import OrderService
        stock_service = StockService()
        order_service = OrderService()

        test_product.units_in_stock = 10
        test_product.reorder_level = 10
        test_product.supplier_id = test_supplier.supplier_id
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
        order_service.ship_order(session, order.order_id)

        session.refresh(test_product)
        assert test_product.units_in_stock == 5
        assert test_product.is_low_stock is True

        alerts = stock_service.get_pending_alerts(session)
        my_alerts = [a for a in alerts if a.supplier_id == test_supplier.supplier_id]
        assert len(my_alerts) == 1
        assert my_alerts[0].product_id == test_product.product_id

        success, msg, updated = stock_service.increase_stock(
            session, test_product.product_id, 20
        )
        assert success is True

        session.refresh(test_product)
        assert test_product.units_in_stock == 25

        success, msg, resolved = stock_service.resolve_alert(
            session, my_alerts[0].alert_id
        )
        assert success is True
        session.refresh(my_alerts[0])
        assert my_alerts[0].status == 'resolved'

        alerts = stock_service.get_pending_alerts(session)
        my_alerts = [a for a in alerts if a.supplier_id == test_supplier.supplier_id]
        assert len(my_alerts) == 0