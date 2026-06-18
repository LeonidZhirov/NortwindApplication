# tests/integration/executor/test_low_stock_scenarios.py
from services import ProductService, StockService
from models import Product


class TestLowStockScenarios:
    def test_detect_low_stock_products(self, session):
        product_service = ProductService()

        product1 = Product(
            product_name="Low Stock Product",
            unit_price=10.0,
            units_in_stock=3,
            reorder_level=10,
            supplier_id=1,
            discontinued=0
        )
        product2 = Product(
            product_name="Normal Stock Product",
            unit_price=15.0,
            units_in_stock=100,
            reorder_level=10,
            supplier_id=1,
            discontinued=0
        )
        session.add_all([product1, product2])
        session.flush()

        low_stock = product_service.get_low_stock_products(session)
        assert len(low_stock) == 1
        assert low_stock[0].product_id == product1.product_id

    def test_auto_create_alerts_for_all_low_stock(self, session):
        stock_service = StockService()

        product1 = Product(
            product_name="Low Stock 1",
            unit_price=10.0,
            units_in_stock=3,
            reorder_level=10,
            supplier_id=1,
            discontinued=0
        )
        product2 = Product(
            product_name="Low Stock 2",
            unit_price=15.0,
            units_in_stock=5,
            reorder_level=10,
            supplier_id=1,
            discontinued=0
        )
        product3 = Product(
            product_name="Normal Stock",
            unit_price=20.0,
            units_in_stock=100,
            reorder_level=10,
            supplier_id=1,
            discontinued=0
        )
        session.add_all([product1, product2, product3])
        session.flush()

        created_count, messages = stock_service.create_alerts_for_all_low_stock(session)
        assert created_count == 2

        from models.stock_alert_model import StockAlert
        alerts = session.query(StockAlert).filter(StockAlert.status == 'pending').all()
        assert len(alerts) == 2
        alert_product_ids = {a.product_id for a in alerts}
        assert product1.product_id in alert_product_ids
        assert product2.product_id in alert_product_ids
        assert product3.product_id not in alert_product_ids

    def test_low_stock_products_with_alerts_display(self, session):
        from models.stock_alert_model import StockAlert
        stock_service = StockService()

        product1 = Product(
            product_name="Low Stock With Alert",
            unit_price=10.0,
            units_in_stock=3,
            reorder_level=10,
            supplier_id=1,
            discontinued=0
        )
        product2 = Product(
            product_name="Low Stock Without Alert",
            unit_price=15.0,
            units_in_stock=5,
            reorder_level=10,
            supplier_id=1,
            discontinued=0
        )
        session.add_all([product1, product2])
        session.flush()

        alert = StockAlert(
            product_id=product1.product_id,
            current_stock=3,
            reorder_level=10,
            supplier_id=1,
            status='pending'
        )
        session.add(alert)
        session.flush()

        low_stock = stock_service.get_low_stock_products(session)
        assert len(low_stock) == 2

        pending_alerts = stock_service.get_pending_alerts(session)
        alert_product_ids = {a.product_id for a in pending_alerts}
        assert product1.product_id in alert_product_ids
        assert product2.product_id not in alert_product_ids