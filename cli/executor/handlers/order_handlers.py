# cli/executor/handlers/order_handlers.py
from datetime import date
from cli.executor.handlers.base import BaseExecutorHandler


class ShowUnshippedOrdersHandler(BaseExecutorHandler):
    def handle(self) -> None:
        self._display_header("НЕОТГРУЖЕННЫЕ ЗАКАЗЫ")

        orders = self._order_service.get_unshipped_orders(self._session)

        if not orders:
            print("\n📭 Нет новых заказов для отгрузки")
        else:
            print(self._display_service.format_orders(orders, with_status=False))

        self._wait()


class ShowOrderDetailsHandler(BaseExecutorHandler):
    def handle(self) -> None:
        order_id = self._input_int("\nВведите ID заказа: ")
        if order_id is None:
            return

        order_summary = self._order_service.get_order_summary(self._session, order_id)

        if not order_summary:
            print(f"\n❌ Заказ #{order_id} не найден")
            self._wait()
            return

        self._display_header(f"ДЕТАЛИ ЗАКАЗА #{order_id}")
        print(self._display_service.format_order_details(order_summary))
        self._wait()


class ShipOrderHandler(BaseExecutorHandler):
    def handle(self) -> None:
        show_handler = ShowUnshippedOrdersHandler(self._session)
        show_handler.handle()

        order_id = self._input_int("\nВведите ID заказа для отгрузки (0 для выхода): ", default=0)
        if order_id is None or order_id == 0:
            return

        can_ship, issues = self._order_service.validate_order_shippable(
            self._session, order_id
        )

        if not can_ship:
            print("\n❌ Невозможно отгрузить заказ:")
            for issue in issues:
                if 'error' in issue:
                    print(f"  - {issue['error']}")
                else:
                    print(
                        f"  - {issue['product_name']}: нужно {issue['required']}, "
                        f"есть {issue['available']} (не хватает {issue['shortage']})"
                    )
            self._wait()
            return

        if not self._confirm(f"\nПодтвердить отгрузку заказа #{order_id}? (y/n): "):
            print("❌ Отгрузка отменена")
            self._wait()
            return

        try:
            shipped_order = self._order_service.ship_order(self._session, order_id)

            print(f"\n✅ Заказ #{order_id} успешно отгружен!")
            print(f"📅 Дата отгрузки: {shipped_order.shipped_date}")

            self._show_new_alerts()

        except ValueError as e:
            print(f"\n❌ Ошибка: {e}")
        except Exception as e:
            print(f"\n❌ Непредвиденная ошибка: {e}")

        self._wait()

    def _show_new_alerts(self) -> None:
        pending_alerts = self._stock_service.get_pending_alerts(self._session)
        today = date.today()
        new_alerts = [
            a for a in pending_alerts
            if a.alert_date and a.alert_date == today
        ]

        if new_alerts:
            print("\n⚠️ СОЗДАНЫ УВЕДОМЛЕНИЯ ДЛЯ ПОСТАВЩИКОВ:")
            for alert in new_alerts:
                product_name = alert.product.product_name if alert.product else "Неизвестный товар"
                print(f"  - Товар '{product_name}' (остаток: {alert.current_stock})")


class ShowShippedHistoryHandler(BaseExecutorHandler):
    def handle(self) -> None:
        self._display_header("ИСТОРИЯ ОТГРУЗОК")

        orders = self._order_service.get_shipped_orders(self._session, limit=20)

        if not orders:
            print("\n📭 Нет отгруженных заказов")
            self._wait()
            return

        print(f"\n{'ID':>5} | {'Дата заказа':<12} | {'Дата отгрузки':<12} | "
              f"{'Клиент':<35} | {'Сумма':>10}")
        print("-" * 85)

        for order in orders:
            total = sum(d.unit_price * d.quantity for d in order.details)
            customer_name = order.customer.company_name if order.customer else 'N/A'
            print(
                f"{order.order_id:>5} | {order.order_date:<12} | "
                f"{order.shipped_date:<12} | {customer_name[:33]:<35} | "
                f"${float(total):>9.2f}"
            )

        self._wait()