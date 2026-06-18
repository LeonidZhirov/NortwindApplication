# cli/executor/role.py
from typing import Dict, Callable, Optional

from cli.base_role import BaseRole
from cli.common.session_manager import SessionManager
from cli.executor.handlers import (
    ShowUnshippedOrdersHandler,
    ShowOrderDetailsHandler,
    ShipOrderHandler,
    ShowShippedHistoryHandler,
    ShowAlertsHandler,
    ShowStatisticsHandler,
    ShowLowStockProductsHandler,
    CreateAlertsHandler,
)
from services import OrderService, StockService


class ExecutorRole(BaseRole):
    def __init__(self, cli_context):
        super().__init__(cli_context)
        self._session_manager = SessionManager()
        self._order_service = OrderService()
        self._stock_service = StockService()

    def _setup_services(self) -> None:
        pass

    def get_role_name(self) -> str:
        return "РЕЖИМ ИСПОЛНИТЕЛЯ 👔 (Менеджер склада)"

    def get_status_info(self) -> Optional[str]:
        with self._session_manager.session() as session:
            unshipped = self._order_service.get_unshipped_orders(session)
            pending_alerts = self._stock_service.get_pending_alerts(session)
            low_stock = self._stock_service.get_low_stock_products(session)

            return (
                f"📊 Статистика:\n"
                f"  📦 Новых заказов: {len(unshipped)}\n"
                f"  ⚠️ Активных уведомлений: {len(pending_alerts)}\n"
                f"  📉 Товаров с низким остатком: {len(low_stock)}"
            )

    def get_menu_items(self) -> Dict[str, tuple[str, Callable]]:
        return {
            '1': ("📋 Просмотреть новые заказы", self._show_unshipped),
            '2': ("🔍 Просмотреть детали заказа", self._show_details),
            '3': ("🚚 Отгрузить заказ", self._ship_order),
            '4': ("📜 История отгрузок", self._show_history),
            '5': ("⚠️ Уведомления поставщикам", self._show_alerts),
            '6': ("📊 Статистика по заказам", self._show_statistics),
            '7': ("📦 Товары с низким остатком", self._show_low_stock),
            '8': ("➕ Создать уведомления о низком остатке", self._create_alerts)
        }

    def _with_session(self, handler_class):
        def wrapper():
            with self._session_manager.session() as session:
                handler = handler_class(session)
                handler.handle()
        return wrapper

    def _show_unshipped(self) -> None:
        self._with_session(ShowUnshippedOrdersHandler)()

    def _show_details(self) -> None:
        self._with_session(ShowOrderDetailsHandler)()

    def _ship_order(self) -> None:
        self._with_session(ShipOrderHandler)()

    def _show_history(self) -> None:
        self._with_session(ShowShippedHistoryHandler)()

    def _show_alerts(self) -> None:
        self._with_session(ShowAlertsHandler)()

    def _show_statistics(self) -> None:
        self._with_session(ShowStatisticsHandler)()

    def _show_low_stock(self) -> None:
        self._with_session(ShowLowStockProductsHandler)()

    def _create_alerts(self) -> None:
        self._with_session(CreateAlertsHandler)()