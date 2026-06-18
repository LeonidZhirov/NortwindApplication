from unittest.mock import Mock

from cli.executor.handlers import ShowShippedHistoryHandler


class TestShowShippedHistoryHandler:
    def test_handle_with_shipped_orders(self, capsys, session, test_shipped_order):
        handler = ShowShippedHistoryHandler(session)
        handler._display_header = lambda x: None
        handler._wait = Mock()

        handler.handle()

        captured = capsys.readouterr()
        assert str(test_shipped_order.order_id) in captured.out
        handler._wait.assert_called_once()

    def test_handle_no_shipped_orders(self, capsys, session):
        handler = ShowShippedHistoryHandler(session)
        handler._display_header = lambda x: None
        handler._wait = Mock()

        handler.handle()

        captured = capsys.readouterr()
        assert "Нет отгруженных заказов" in captured.out
        handler._wait.assert_called_once()