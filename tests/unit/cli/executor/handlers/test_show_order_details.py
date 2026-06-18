from unittest.mock import Mock

from cli.executor.handlers import ShowOrderDetailsHandler


class TestShowOrderDetailsHandler:
    def test_handle_with_valid_order(self, capsys, session, test_order):
        handler = ShowOrderDetailsHandler(session)
        handler._display_header = lambda x: None
        handler._wait = lambda: None
        handler._input_int = Mock(return_value=test_order.order_id)

        handler.handle()

        captured = capsys.readouterr()
        assert str(test_order.order_id) in captured.out

    def test_handle_with_invalid_order(self, capsys, session):
        handler = ShowOrderDetailsHandler(session)
        handler._display_header = lambda x: None
        handler._wait = Mock()
        handler._input_int = Mock(return_value=999)

        handler.handle()

        handler._wait.assert_called_once()

    def test_handle_cancel(self, session):
        handler = ShowOrderDetailsHandler(session)
        handler._display_header = lambda x: None
        handler._wait = Mock()
        handler._input_int = Mock(return_value=None)

        handler.handle()

        handler._wait.assert_not_called()