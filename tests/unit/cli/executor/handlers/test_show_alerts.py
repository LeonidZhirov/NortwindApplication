from unittest.mock import Mock

from cli.executor.handlers import ShowAlertsHandler

#TODO One test failed
class TestShowAlertsHandler:
    def test_handle_with_alerts(self, capsys, session, test_stock_alert):
        handler = ShowAlertsHandler(session)
        handler._display_header = lambda x: None
        handler._wait = Mock()
        handler._input_choice = Mock(return_value=0)

        handler.handle()

        captured = capsys.readouterr()
        assert str(test_stock_alert.alert_id) in captured.out
        handler._wait.assert_called_once()

    def test_handle_no_alerts(self, capsys, session):
        handler = ShowAlertsHandler(session)
        handler._display_header = lambda x: None
        handler._wait = Mock()
        handler._input_choice = Mock(return_value=0)

        handler.handle()

        captured = capsys.readouterr()
        assert "Нет активных уведомлений" in captured.out
        handler._wait.assert_called_once()

    def test_handle_resolve_all_alerts_success(self, session, test_stock_alert):
        handler = ShowAlertsHandler(session)
        handler._display_header = lambda x: None
        handler._wait = Mock()
        handler._input_choice = Mock(return_value=1)

        handler.handle()

        session.refresh(test_stock_alert)
        assert test_stock_alert.status == 'resolved'
        handler._wait.assert_called_once()

    def test_handle_resolve_all_alerts_partial(self, session, test_product):
        from models.stock_alert_model import StockAlert

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

        from models.product_model import Product
        from models.supplier_model import Supplier

        supplier2 = Supplier(
            company_name="Test Supplier 2",
            contact_name="Test Contact 2",
            country="Test Country"
        )
        session.add(supplier2)
        session.flush()

        product2 = Product(
            product_name="Normal Stock",
            unit_price=20.0,
            units_in_stock=100,
            reorder_level=10,
            supplier_id=supplier2.supplier_id,
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
        session.add_all([alert1, alert2])
        session.flush()

        handler = ShowAlertsHandler(session)
        handler._display_header = lambda x: None
        handler._wait = Mock()
        handler._input_choice = Mock(return_value=1)

        handler.handle()

        session.refresh(alert1)
        session.refresh(alert2)
        assert alert1.status == 'pending'
        assert alert2.status == 'resolved'
        handler._wait.assert_called_once()

    def test_handle_resolve_single_alert_success(self, session, test_stock_alert):
        handler = ShowAlertsHandler(session)
        handler._display_header = lambda x: None
        handler._wait = Mock()
        handler._input_choice = Mock(return_value=2)
        handler._input_int = Mock(return_value=test_stock_alert.alert_id)

        handler.handle()

        session.refresh(test_stock_alert)
        assert test_stock_alert.status == 'resolved'
        handler._wait.assert_called_once()

    def test_handle_resolve_single_alert_fail_low_stock(self, session, test_stock_alert, test_product):
        test_product.units_in_stock = 3
        test_product.reorder_level = 10
        session.flush()

        handler = ShowAlertsHandler(session)
        handler._display_header = lambda x: None
        handler._wait = Mock()
        handler._input_choice = Mock(return_value=2)
        handler._input_int = Mock(return_value=test_stock_alert.alert_id)

        handler.handle()

        session.refresh(test_stock_alert)
        assert test_stock_alert.status == 'pending'
        handler._wait.assert_called_once()