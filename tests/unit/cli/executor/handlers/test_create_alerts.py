from unittest.mock import Mock, patch

from cli.executor.handlers import CreateAlertsHandler
from models.stock_alert_model import StockAlert

class TestCreateAlertsHandler:
    def test_handle_no_low_stock(self, capsys, session, test_product):
        test_product.units_in_stock = 100
        test_product.reorder_level = 10
        session.flush()

        handler = CreateAlertsHandler(session)
        handler._display_header = lambda x: None
        handler._wait = Mock()

        handler.handle()

        captured = capsys.readouterr()
        assert "Все товары в достаточном количестве" in captured.out
        handler._wait.assert_called_once()

    def test_handle_with_low_stock(self, capsys, session, test_product):
        test_product.units_in_stock = 5
        test_product.reorder_level = 10
        session.flush()

        handler = CreateAlertsHandler(session)
        handler._display_header = lambda x: None
        handler._wait = Mock()
        handler._input_choice = Mock(return_value=0)

        handler.handle()

        captured = capsys.readouterr()
        assert test_product.product_name in captured.out
        handler._wait.assert_called_once()

    @patch('builtins.input')
    def test_create_all_alerts(self, mock_input, session, test_product):
        test_product.units_in_stock = 5
        test_product.reorder_level = 10
        session.flush()

        handler = CreateAlertsHandler(session)
        handler._display_header = lambda x: None
        handler._wait = Mock()
        handler._input_choice = Mock(return_value=1)

        handler.handle()

        alerts = session.query(StockAlert).filter(
            StockAlert.product_id == test_product.product_id
        ).all()
        assert len(alerts) == 1
        assert alerts[0].status == 'pending'

    @patch('builtins.input')
    def test_create_single_alert(self, mock_input, session, test_product):
        test_product.units_in_stock = 5
        test_product.reorder_level = 10
        session.flush()

        handler = CreateAlertsHandler(session)
        handler._display_header = lambda x: None
        handler._wait = Mock()
        handler._input_choice = Mock(return_value=2)
        mock_input.return_value = str(test_product.product_id)

        handler.handle()

        alerts = session.query(StockAlert).filter(
            StockAlert.product_id == test_product.product_id
        ).all()
        assert len(alerts) == 1
        assert alerts[0].status == 'pending'

    @patch('builtins.input')
    def test_create_single_alert_already_exists(self, mock_input, capsys, session, test_product, test_stock_alert):
        test_product.units_in_stock = 5
        test_product.reorder_level = 10
        session.flush()

        handler = CreateAlertsHandler(session)
        handler._display_header = lambda x: None
        handler._wait = Mock()
        handler._input_choice = Mock(return_value=2)
        mock_input.return_value = str(test_product.product_id)

        handler.handle()

        captured = capsys.readouterr()
        assert "уже есть активные уведомления" in captured.out

    @patch('builtins.input')
    def test_create_single_alert_no_available(self, mock_input, capsys, session, test_product, test_stock_alert):
        test_product.units_in_stock = 5
        test_product.reorder_level = 10
        session.flush()

        handler = CreateAlertsHandler(session)
        handler._display_header = lambda x: None
        handler._wait = Mock()
        handler._input_choice = Mock(return_value=2)

        handler.handle()

        captured = capsys.readouterr()
        assert "уже есть активные уведомления" in captured.out
        handler._wait.assert_called_once()