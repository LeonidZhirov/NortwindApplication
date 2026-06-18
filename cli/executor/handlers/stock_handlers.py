# cli/executor/handlers/stock_handlers.py
from cli.executor.handlers.base import BaseExecutorHandler
from models import StockAlert, Product
from typing import List


class ShowAlertsHandler(BaseExecutorHandler):
    ACTION_BACK = 0
    ACTION_RESOLVE_ALL = 1
    ACTION_RESOLVE_SINGLE = 2

    def handle(self) -> None:
        self._display_header("УВЕДОМЛЕНИЯ ПОСТАВЩИКАМ")

        alerts = self._stock_service.get_pending_alerts(self._session)
        print(self._display_service.format_alerts(alerts))

        if not alerts:
            self._wait()
            return

        self._show_actions(alerts)
        self._wait()

    def _show_actions(self, alerts: List[StockAlert]) -> None:
        """Показать доступные действия с уведомлениями."""
        print("\nДействия:")
        print(f"  {self.ACTION_RESOLVE_ALL}. Отметить все возможные уведомления как обработанные")
        print(f"  {self.ACTION_RESOLVE_SINGLE}. Отметить конкретное уведомление как обработанное")
        print(f"  {self.ACTION_BACK}. Вернуться")

        action = self._input_choice("\nВаш выбор: ", 2)

        if action == self.ACTION_BACK:
            return
        elif action == self.ACTION_RESOLVE_ALL:
            self._resolve_all_alerts()
        elif action == self.ACTION_RESOLVE_SINGLE:
            self._resolve_single_alert(alerts)

    def _resolve_all_alerts(self) -> None:
        """Обработка всех уведомлений."""
        count, messages = self._stock_service.resolve_all_alerts(self._session)

        if count > 0:
            print(f"\n✅ Успешно обработано {count} уведомлений")
        else:
            print("\nℹ️ Ни одно уведомление не может быть закрыто (товары всё ещё требуют пополнения)")

        for msg in messages:
            print(f"  {msg}")

    def _resolve_single_alert(self, alerts: List[StockAlert]) -> None:
        alert_ids = [str(a.alert_id) for a in alerts]
        print(f"\nДоступные уведомления: {', '.join(alert_ids)}")

        alert_id = self._input_int("Введите ID уведомления: ")
        if alert_id is None:
            return

        success, msg, _ = self._stock_service.resolve_alert(self._session, alert_id)
        print(f"{'✅' if success else '❌'} {msg}")


class ShowLowStockProductsHandler(BaseExecutorHandler):
    def handle(self) -> None:
        self._display_header("ТОВАРЫ С НИЗКИМ ОСТАТКОМ")

        products = self._stock_service.get_low_stock_products(self._session)
        print(self._display_service.format_low_stock_products(products))
        self._wait()


class CreateAlertsHandler(BaseExecutorHandler):
    ACTION_BACK = 0
    ACTION_CREATE_ALL = 1
    ACTION_CREATE_SINGLE = 2

    def handle(self) -> None:
        self._display_header("СОЗДАНИЕ УВЕДОМЛЕНИЙ ПОСТАВЩИКАМ")

        # Показываем товары с низким остатком
        low_stock = self._stock_service.get_low_stock_products(self._session)

        if not low_stock:
            print("\n✅ Все товары в достаточном количестве. Уведомления не требуются.")
            self._wait()
            return

        print(self._display_service.format_low_stock_products(low_stock))

        pending_alerts = self._stock_service.get_pending_alerts(self._session)
        alert_product_ids = {a.product_id for a in pending_alerts}

        already_alerted = [p for p in low_stock if p.product_id in alert_product_ids]
        if already_alerted:
            print("\n⚠️ Для следующих товаров уже есть активные уведомления:")
            for product in already_alerted:
                print(f"  - {product.product_name}")

        self._show_actions(low_stock, alert_product_ids)
        self._wait()

    def _show_actions(self, low_stock: List[Product], alert_product_ids: set) -> None:
        print("\nДействия:")
        print(f"  {self.ACTION_CREATE_ALL}. Создать уведомления для всех товаров с низким остатком")
        print(f"  {self.ACTION_CREATE_SINGLE}. Создать уведомление для конкретного товара")
        print(f"  {self.ACTION_BACK}. Вернуться")

        action = self._input_choice("\nВаш выбор: ", 2)

        if action == self.ACTION_BACK:
            return
        elif action == self.ACTION_CREATE_ALL:
            self._create_all_alerts()
        elif action == self.ACTION_CREATE_SINGLE:
            self._create_single_alert(low_stock, alert_product_ids)

    def _create_all_alerts(self) -> None:
        count, messages = self._stock_service.create_alerts_for_all_low_stock(self._session)

        if count > 0:
            print(f"\n✅ Создано {count} уведомлений")
        else:
            print("\nℹ️ Новые уведомления не созданы (возможно, для всех товаров уже есть уведомления)")

        for msg in messages:
            print(f"  {msg}")

    def _create_single_alert(self, low_stock: List[Product], alert_product_ids: set) -> None:
        product_ids = [str(p.product_id) for p in low_stock if p.product_id not in alert_product_ids]

        if not product_ids:
            print("\nℹ️ Для всех товаров с низким остатком уже есть активные уведомления")
            return

        print(f"\nДоступные товары для создания уведомлений: {', '.join(product_ids)}")

        product_id = self._input_int("Введите ID товара: ")
        if product_id is None:
            return

        success, msg, _ = self._stock_service.create_alert_for_product(self._session, product_id)
        print(f"{'✅' if success else '❌'} {msg}")