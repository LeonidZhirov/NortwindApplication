# cli/executor/handlers/statistics_handlers.py
from cli.executor.handlers.base import BaseExecutorHandler


class ShowStatisticsHandler(BaseExecutorHandler):
    def handle(self) -> None:
        self._display_header("СТАТИСТИКА ЗАКАЗОВ")

        stats = self._order_service.get_statistics(self._session)
        print(self._display_service.format_statistics(stats))
        self._wait()