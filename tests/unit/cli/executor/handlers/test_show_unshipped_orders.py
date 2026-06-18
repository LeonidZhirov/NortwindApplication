from cli.executor.handlers import ShowUnshippedOrdersHandler


class TestShowUnshippedOrdersHandler:
    def test_handle_with_unshipped_orders(self, capsys, session, test_order):
        handler = ShowUnshippedOrdersHandler(session)
        handler._display_header = lambda x: None
        handler._wait = lambda: None

        handler.handle()

        captured = capsys.readouterr()
        assert str(test_order.order_id) in captured.out

    def test_handle_no_unshipped_orders(self, capsys, session):
        handler = ShowUnshippedOrdersHandler(session)
        handler._display_header = lambda x: None
        handler._wait = lambda: None

        handler.handle()

        captured = capsys.readouterr()
        assert "Нет новых заказов" in captured.out