# tests/integration/executor/test_alert_scenarios.py
from services import StockService
from models import StockAlert, Product


class TestAlertScenarios:
    def test_create_alert_for_low_stock_product(self, session, test_product):
        stock_service = StockService()

        test_product.units_in_stock = 5
        test_product.reorder_level = 10
        session.flush()

        success, msg, alert = stock_service.create_alert_for_product(
            session, test_product.product_id
        )
        assert success is True
        assert alert is not None
        assert alert.status == 'pending'
        assert alert.current_stock == 5
        assert alert.reorder_level == 10

    def test_create_alert_for_product_with_sufficient_stock_fails(self, session, test_product):
        stock_service = StockService()

        test_product.units_in_stock = 100
        test_product.reorder_level = 10
        session.flush()

        success, msg, alert = stock_service.create_alert_for_product(
            session, test_product.product_id
        )
        assert success is False
        assert alert is None
        assert "не требует пополнения" in msg

    def test_create_alert_duplicate_prevention(self, session, test_product):
        stock_service = StockService()

        test_product.units_in_stock = 5
        test_product.reorder_level = 10
        session.flush()

        success1, msg1, alert1 = stock_service.create_alert_for_product(
            session, test_product.product_id
        )
        assert success1 is True

        success2, msg2, alert2 = stock_service.create_alert_for_product(
            session, test_product.product_id
        )
        assert success2 is False
        assert "уже есть активное уведомление" in msg2

    def test_resolve_alert_after_restock(self, session, test_product, test_stock_alert):
        stock_service = StockService()

        test_product.units_in_stock = 20
        test_product.reorder_level = 10
        session.flush()

        success, msg, alert = stock_service.resolve_alert(
            session, test_stock_alert.alert_id
        )
        assert success is True
        session.refresh(test_stock_alert)
        assert test_stock_alert.status == 'resolved'

    def test_resolve_alert_fails_if_still_low(self, session, test_product, test_stock_alert):
        stock_service = StockService()

        test_product.units_in_stock = 5
        test_product.reorder_level = 10
        session.flush()

        success, msg, alert = stock_service.resolve_alert(
            session, test_stock_alert.alert_id
        )
        assert success is False
        assert "всё ещё требует пополнения" in msg
        session.refresh(test_stock_alert)
        assert test_stock_alert.status == 'pending'

    def test_resolve_all_alerts_partial(self, session, test_product):
        stock_service = StockService()

        test_product.units_in_stock = 3
        test_product.reorder_level = 10
        session.flush()

        alert1 = StockAlert(
            product_id=test_product.product_id,
            current_stock=3,
            reorder_level=10,
            supplier_id=test_product.supplier_id,
            status='pending'
        )
        session.add(alert1)
        session.flush()

        product2 = Product(
            product_name="Normal Stock",
            unit_price=15.0,
            units_in_stock=100,
            reorder_level=10,
            supplier_id=test_product.supplier_id,
            discontinued=0
        )
        session.add(product2)
        session.flush()

        alert2 = StockAlert(
            product_id=product2.product_id,
            current_stock=100,
            reorder_level=10,
            supplier_id=product2.supplier_id,
            status='pending'
        )
        session.add(alert2)
        session.flush()

        test_product.units_in_stock = 7
        session.flush()

        resolved_count, messages = stock_service.resolve_all_alerts(session)

        assert resolved_count == 1

        session.refresh(alert1)
        session.refresh(alert2)
        assert alert1.status == 'pending'
        assert alert2.status == 'resolved'