from unittest.mock import Mock, patch
from datetime import date

from cli.executor.handlers import ShipOrderHandler


class TestShipOrderHandler:
    @patch('cli.executor.handlers.order_handlers.ShowUnshippedOrdersHandler')
    def test_handle_success(self, mock_show_unshipped, capsys, session, test_order, test_product):
        handler = ShipOrderHandler(session)
        handler._display_header = lambda x: None
        handler._wait = Mock()
        handler._input_int = Mock(return_value=test_order.order_id)
        handler._confirm = Mock(return_value=True)

        mock_show_unshipped.return_value.handle = Mock()

        handler.handle()

        session.refresh(test_order)
        assert test_order.shipped_date == date.today()
        handler._wait.assert_called_once()

    @patch('cli.executor.handlers.order_handlers.ShowUnshippedOrdersHandler')
    def test_handle_cancel_shipment(self, mock_show_unshipped, session, test_order):
        handler = ShipOrderHandler(session)
        handler._display_header = lambda x: None
        handler._wait = Mock()
        handler._input_int = Mock(return_value=test_order.order_id)
        handler._confirm = Mock(return_value=False)

        mock_show_unshipped.return_value.handle = Mock()

        handler.handle()

        session.refresh(test_order)
        assert test_order.shipped_date is None
        handler._wait.assert_called_once()

    @patch('cli.executor.handlers.order_handlers.ShowUnshippedOrdersHandler')
    def test_handle_cancel_input(self, mock_show_unshipped, session):
        handler = ShipOrderHandler(session)
        handler._display_header = lambda x: None
        handler._wait = Mock()
        handler._input_int = Mock(return_value=0)

        mock_show_unshipped.return_value.handle = Mock()

        handler.handle()

        handler._wait.assert_not_called()

    @patch('cli.executor.handlers.order_handlers.ShowUnshippedOrdersHandler')
    def test_handle_insufficient_stock(self, mock_show_unshipped, capsys, session, test_order, test_product):
        test_product.units_in_stock = 1
        session.flush()

        handler = ShipOrderHandler(session)
        handler._display_header = lambda x: None
        handler._wait = Mock()
        handler._input_int = Mock(return_value=test_order.order_id)
        handler._confirm = Mock(return_value=True)

        mock_show_unshipped.return_value.handle = Mock()

        handler.handle()

        captured = capsys.readouterr()
        assert "Невозможно отгрузить заказ" in captured.out
        handler._wait.assert_called_once()