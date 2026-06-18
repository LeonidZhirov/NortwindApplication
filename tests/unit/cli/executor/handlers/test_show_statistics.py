from unittest.mock import Mock

from cli.executor.handlers import ShowStatisticsHandler


class TestShowStatisticsHandler:
    def test_handle(self, capsys, session):
        handler = ShowStatisticsHandler(session)
        handler._display_header = lambda x: None
        handler._wait = Mock()

        handler.handle()

        captured = capsys.readouterr()
        assert "Всего заказов" in captured.out
        handler._wait.assert_called_once()