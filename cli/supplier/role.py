# cli/supplier/role.py
from typing import Dict, Callable, Optional

from cli.base_role import BaseRole
from cli.common.session_manager import SessionManager
from cli.supplier.handlers import (
    SelectSupplierHandler,
    ShowRestockRequestsHandler,
    RestockProductsHandler,
    ShowMyProductsHandler,
    SearchMyProductsHandler,
    ShowSupplierStatisticsHandler,
    ShowRestockHistoryHandler,
    ShowRestockRecommendationsHandler
)
from services import ProductService, StockService
from repositories import SupplierRepository


class SupplierRole(BaseRole):
    def __init__(self, cli_context):
        super().__init__(cli_context)
        self._session_manager = SessionManager()
        self._product_service = ProductService()
        self._stock_service = StockService()
        self._supplier_repo = SupplierRepository()
        self._supplier_id: Optional[int] = None

    def _setup_services(self) -> None:
        pass

    def get_role_name(self) -> str:
        return "РЕЖИМ ПОСТАВЩИКА 📦"

    def get_status_info(self) -> Optional[str]:
        if not self._supplier_id:
            return "⚠️ Поставщик не выбран. Выберите поставщика (пункт 6)"

        with self._session_manager.session() as session:
            supplier = self._supplier_repo.get_by_id(session, self._supplier_id)
            if not supplier:
                return "⚠️ Поставщик не найден"

            products = self._product_service.get_products_by_supplier(session, self._supplier_id)

            total_products = len(products)
            active_products = len([p for p in products if not p.discontinued])
            low_stock = [p for p in products if p.is_low_stock]
            out_of_stock = [p for p in products if (p.units_in_stock or 0) == 0]

            total_value = sum(
                (p.units_in_stock or 0) * (p.unit_price or 0)
                for p in products
            )

            pending_alerts = self._stock_service.get_pending_alerts(session)
            my_alerts = [a for a in pending_alerts if a.supplier_id == self._supplier_id]

            return (f"🏢 Поставщик: {supplier.company_name}\n"
                    f"📍 Страна: {supplier.country or 'Не указана'}\n"
                    f"📦 Всего товаров: {total_products} (активных: {active_products})\n"
                    f"⚠️ Требуют пополнения: {len(low_stock)} (из них нет в наличии: {len(out_of_stock)})\n"
                    f"💰 Общая стоимость на складе: ${float(total_value):,.2f}\n"
                    f"📋 Активных заявок: {len(my_alerts)}")

    def get_menu_items(self) -> Dict[str, tuple[str, Callable]]:
        return {
            '1': ("📋 Просмотреть заявки на пополнение", self._show_restock_requests),
            '2': ("📦 Пополнить товары", self._restock_products),
            '3': ("📊 Мои товары", self._show_my_products),
            '4': ("🔍 Поиск по моим товарам", self._search_my_products),
            '5': ("📈 Статистика поставок", self._show_statistics),
            '6': ("🔄 Сменить поставщика", self._select_supplier),
            '7': ("📋 История пополнений", self._show_restock_history),
            '8': ("💡 Рекомендации по пополнению", self._show_recommendations),
        }

    def _with_session(self, handler_class, *args, **kwargs):
        def wrapper():
            with self._session_manager.session() as session:
                handler = handler_class(session)
                handler.handle(*args, **kwargs)
        return wrapper

    def _require_supplier(self) -> bool:
        if not self._supplier_id:
            print("\n❌ Сначала выберите поставщика (пункт 6)")
            self._wait()
            return False
        return True

    def _select_supplier(self) -> None:
        with self._session_manager.session() as session:
            handler = SelectSupplierHandler(session)
            result = handler.handle()
            if result:
                self._supplier_id = result

    def _show_restock_requests(self) -> None:
        if not self._require_supplier():
            return
        self._with_session(ShowRestockRequestsHandler, self._supplier_id)()

    def _restock_products(self) -> None:
        if not self._require_supplier():
            return
        self._with_session(RestockProductsHandler, self._supplier_id)()

    def _show_my_products(self) -> None:
        if not self._require_supplier():
            return
        self._with_session(ShowMyProductsHandler, self._supplier_id)()

    def _search_my_products(self) -> None:
        if not self._require_supplier():
            return
        self._with_session(SearchMyProductsHandler, self._supplier_id)()

    def _show_statistics(self) -> None:
        if not self._require_supplier():
            return
        self._with_session(ShowSupplierStatisticsHandler, self._supplier_id)()

    def _show_restock_history(self) -> None:
        if not self._require_supplier():
            return
        self._with_session(ShowRestockHistoryHandler, self._supplier_id)()

    def _show_recommendations(self) -> None:
        if not self._require_supplier():
            return
        self._with_session(ShowRestockRecommendationsHandler, self._supplier_id)()

    def run(self) -> None:
        self._select_supplier()
        if self._supplier_id:
            super().run()