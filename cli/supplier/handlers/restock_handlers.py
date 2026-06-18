# cli/supplier/handlers/restock_handlers.py
from typing import List, Any, Dict
from datetime import date

from cli.supplier.handlers.base import BaseSupplierHandler
from models import Product


class ShowRestockRequestsHandler(BaseSupplierHandler):
    ACTION_BACK = 0
    ACTION_AUTO_RESTOCK_ALL = 1
    ACTION_RESTOCK_SELECTED = 2

    def handle(self, supplier_id: int) -> None:
        self._display_header("ЗАЯВКИ НА ПОПОЛНЕНИЕ")

        alerts = self._stock_service.get_pending_alerts(self._session)
        my_alerts = [a for a in alerts if a.supplier_id == supplier_id]

        if not my_alerts:
            print("\n✅ Нет активных заявок на пополнение")
            print("   Все товары в достаточном количестве")
            self._wait()
            return

        print(self._display_service.format_alerts(my_alerts))

        print("\n" + "=" * 80)
        print("💡 Действия с заявками:")
        print(f"  {self.ACTION_AUTO_RESTOCK_ALL}. Пополнить все товары автоматически")
        print(f"  {self.ACTION_RESTOCK_SELECTED}. Пополнить выбранный товар")
        print(f"  {self.ACTION_BACK}. Вернуться")

        action = self._input_choice("\nВаш выбор: ", 2)

        if action == self.ACTION_AUTO_RESTOCK_ALL:
            self._auto_restock_all(my_alerts)
        elif action == self.ACTION_RESTOCK_SELECTED:
            self._restock_selected_alert(my_alerts)

        self._wait()

    def _auto_restock_all(self, alerts: List) -> None:
        restocked = []
        failed = []

        for alert in alerts:
            try:
                product = self._product_service.get_product(self._session, alert.product_id)
                if not product:
                    failed.append((alert.product_id, "Товар не найден"))
                    continue

                target_stock = (product.reorder_level or 0) * 2
                current_stock = product.units_in_stock or 0
                quantity = max(target_stock - current_stock, product.reorder_level or 0)

                if quantity <= 0:
                    continue

                success, msg, updated = self._stock_service.increase_stock(
                    self._session, alert.product_id, quantity
                )

                if success and updated:
                    self._stock_service.resolve_alert(self._session, alert.alert_id)
                    restocked.append({
                        'product_name': product.product_name,
                        'quantity': quantity,
                        'new_stock': updated.units_in_stock
                    })
                else:
                    failed.append((alert.product_id, msg))

            except Exception as e:
                failed.append((alert.product_id, str(e)))

        self._show_restock_results(restocked, failed)

    def _show_restock_results(self, restocked: List, failed: List) -> None:
        if restocked:
            print("\n✅ Успешно пополнены:")
            for item in restocked:
                print(f"  - {item['product_name']}: +{item['quantity']} шт. "
                      f"(новый остаток: {item['new_stock']})")

        if failed:
            print("\n❌ Ошибки при пополнении:")
            for product_id, error in failed:
                print(f"  - Товар #{product_id}: {error}")

    def _restock_selected_alert(self, alerts: List) -> None:
        alert_id = self._input_int("\nВведите ID заявки для обработки (0 для выхода): ", default=0)
        if alert_id is None or alert_id == 0:
            return

        alert = next((a for a in alerts if a.alert_id == alert_id), None)
        if not alert:
            print("❌ Заявка не найдена")
            return

        product = self._product_service.get_product(self._session, alert.product_id)
        if not product:
            print("❌ Товар не найден")
            return

        self._display_product_restock_info(product)

        quantity = self._input_int(
            f"Введите количество для пополнения (0 для отмены): ",
            validator=lambda x: x >= 0
        )

        if quantity is None or quantity <= 0:
            print("❌ Пополнение отменено")
            return

        success, msg, updated = self._stock_service.increase_stock(
            self._session, product.product_id, quantity
        )

        if success and updated:
            self._stock_service.resolve_alert(self._session, alert.alert_id)
            print(f"\n✅ Товар '{product.product_name}' пополнен на {quantity} шт.")
            print(f"📊 Новый остаток: {updated.units_in_stock} шт.")
            print(f"📅 Дата пополнения: {date.today()}")
        else:
            print(f"❌ {msg}")

    def _display_product_restock_info(self, product: Product) -> None:
        print(f"\n📦 Товар: {product.product_name}")
        print(f"📊 Текущий остаток: {product.units_in_stock or 0} шт.")
        print(f"📊 Порог пополнения: {product.reorder_level or 0} шт.")

        suggested = (product.reorder_level or 0) * 2 - (product.units_in_stock or 0)
        recommended = max(suggested, product.reorder_level or 0)
        print(f"💡 Рекомендуемое количество: {recommended} шт.")


class RestockProductsHandler(BaseSupplierHandler):
    def handle(self, supplier_id: int) -> None:
        self._display_header("ПОПОЛНЕНИЕ ТОВАРОВ")

        products = self._product_service.get_products_by_supplier(self._session, supplier_id)

        if not products:
            print("\n📭 У вас пока нет товаров")
            self._wait()
            return

        low_stock, normal, out_of_stock = self._categorize_products(products)
        self._display_product_stats(low_stock, normal, out_of_stock)

        if not low_stock:
            print("\n✅ Все товары в достаточном количестве")
            self._wait()
            return

        self._display_low_stock_products(low_stock)

        product_id = self._input_int("\nВведите ID товара для пополнения (0 для выхода): ", default=0)
        if product_id is None or product_id == 0:
            return

        product = next((p for p in low_stock if p.product_id == product_id), None)
        if not product:
            print("❌ Товар не требует пополнения или не найден")
            self._wait()
            return

        self._perform_restock(product)
        self._wait()

    def _categorize_products(self, products: List[Product]) -> tuple:
        low_stock = []
        normal = []
        out_of_stock = []

        for product in products:
            if product.discontinued:
                continue
            if product.is_low_stock:
                low_stock.append(product)
            elif (product.units_in_stock or 0) == 0:
                out_of_stock.append(product)
            else:
                normal.append(product)

        return low_stock, normal, out_of_stock

    def _display_product_stats(self, low_stock: List, normal: List, out_of_stock: List) -> None:
        print(f"\n📊 Статистика товаров:")
        print(f"  ✅ В наличии: {len(normal)}")
        print(f"  ⚠️ Низкий остаток: {len(low_stock)}")
        print(f"  ❌ Нет в наличии: {len(out_of_stock)}")

    def _display_low_stock_products(self, products: List[Product]) -> None:
        print("\n" + "=" * 80)
        print("📦 ТОВАРЫ, ТРЕБУЮЩИЕ ПОПОЛНЕНИЯ:")
        print("-" * 80)
        for product in products:
            suggested = (product.reorder_level or 0) * 2 - (product.units_in_stock or 0)
            print(
                f"  ID: {product.product_id:>3} | {product.product_name:<40} | "
                f"Остаток: {product.units_in_stock or 0:>3} | "
                f"Порог: {product.reorder_level or 0:>3} | "
                f"Рекомендуется: {max(suggested, product.reorder_level or 0)}"
            )

    def _perform_restock(self, product: Product) -> None:
        suggested = (product.reorder_level or 0) * 2 - (product.units_in_stock or 0)
        recommended = max(suggested, product.reorder_level or 0)

        print(f"\n📦 Товар: {product.product_name}")
        print(f"💰 Цена: ${float(product.unit_price or 0):.2f}")
        print(f"📊 Текущий остаток: {product.units_in_stock or 0} шт.")
        print(f"📊 Порог пополнения: {product.reorder_level or 0} шт.")
        print(f"💡 Рекомендуемое количество: {recommended} шт.")

        quantity = self._input_int(f"\nВведите количество для закупки: ", validator=lambda x: x > 0)
        if quantity is None or quantity <= 0:
            print("❌ Количество должно быть больше 0")
            return

        success, msg, updated = self._stock_service.increase_stock(
            self._session, product.product_id, quantity
        )

        if success and updated:
            print(f"\n✅ Товар '{product.product_name}' пополнен на {quantity} шт.")
            print(f"📊 Новый остаток: {updated.units_in_stock} шт.")

            self._resolve_alerts_for_product(product.product_id)
        else:
            print(f"❌ {msg}")

    def _resolve_alerts_for_product(self, product_id: int) -> None:
        alerts = self._stock_service.get_pending_alerts(self._session)
        resolved_count = 0

        for alert in alerts:
            if alert.product_id == product_id:
                success, msg, _ = self._stock_service.resolve_alert(self._session, alert.alert_id)
                if success:
                    resolved_count += 1

        if resolved_count > 0:
            print(f"✅ {resolved_count} заявок отмечены как выполненные")

class ShowRestockHistoryHandler(BaseSupplierHandler):
    def handle(self, supplier_id: int) -> None:
        self._display_header("ИСТОРИЯ ПОПОЛНЕНИЙ")

        print("\n⏳ Функционал в разработке")
        print("   История пополнений будет доступна в следующей версии")

        alerts = self._stock_service.get_pending_alerts(self._session)
        my_alerts = [a for a in alerts if a.supplier_id == supplier_id]

        if my_alerts:
            print(f"\n📋 Активных заявок: {len(my_alerts)}")
            print("   (для просмотра используйте пункт 1)")

        self._wait()


class ShowRestockRecommendationsHandler(BaseSupplierHandler):
    def handle(self, supplier_id: int) -> None:
        self._display_header("РЕКОМЕНДАЦИИ ПО ПОПОЛНЕНИЮ")

        products = self._product_service.get_products_by_supplier(self._session, supplier_id)

        needs_restock = self._analyze_products(products)

        if not needs_restock:
            print("\n✅ Все товары в достаточном количестве")
            print("   Рекомендации по пополнению не требуются")
            self._wait()
            return

        self._display_recommendations(needs_restock)

        if self._confirm("\n💡 Выполнить автоматическое пополнение всех товаров? (y/n): "):
            self._auto_restock_all(needs_restock)

        self._wait()

    def _analyze_products(self, products: List[Product]) -> List[Dict[str, Any]]:
        needs_restock = []

        for product in products:
            if product.discontinued:
                continue

            current = product.units_in_stock or 0
            reorder = product.reorder_level or 0

            if current <= reorder:
                recommended = max(reorder * 2 - current, reorder)

                if current == 0:
                    priority = "Высокий"
                elif current < reorder / 2:
                    priority = "Средний"
                else:
                    priority = "Низкий"

                needs_restock.append({
                    'product': product,
                    'current': current,
                    'reorder': reorder,
                    'recommended': recommended,
                    'priority': priority
                })

        priority_order = {'Высокий': 0, 'Средний': 1, 'Низкий': 2}
        needs_restock.sort(key=lambda x: priority_order[x['priority']])

        return needs_restock

    def _display_recommendations(self, needs_restock: List[Dict[str, Any]]) -> None:
        print("\n📋 РЕКОМЕНДАЦИИ ПО ПОПОЛНЕНИЮ:")
        print("-" * 80)
        print(f"{'ID':>3} | {'Товар':<40} | {'Остаток':>6} | {'Порог':>5} | "
              f"{'Рекомендуется':>12} | {'Приоритет':<8}")
        print("-" * 80)

        total_recommended = 0
        for item in needs_restock:
            print(f"{item['product'].product_id:>3} | {item['product'].product_name[:38]:<40} | "
                  f"{item['current']:>6} | {item['reorder']:>5} | "
                  f"{item['recommended']:>12} | {item['priority']:<8}")
            total_recommended += item['recommended']

        print("-" * 80)
        print(f"📊 Рекомендуется пополнить: {len(needs_restock)} товаров")
        print(f"📦 Общее количество: {total_recommended} шт.")

    def _auto_restock_all(self, needs_restock: List[Dict[str, Any]]) -> None:
        restocked_count = 0

        for item in needs_restock:
            success, msg, updated = self._stock_service.increase_stock(
                self._session,
                item['product'].product_id,
                item['recommended']
            )

            if success and updated:
                alerts = self._stock_service.get_pending_alerts(self._session)
                for alert in alerts:
                    if alert.product_id == item['product'].product_id:
                        self._stock_service.resolve_alert(self._session, alert.alert_id)
                restocked_count += 1

        print(f"\n✅ Автоматически пополнено {restocked_count} товаров")
        print("   Все заявки отмечены как обработанные")


class ShowRestockHistoryHandler(BaseSupplierHandler):
    def handle(self, supplier_id: int) -> None:
        self._display_header("ИСТОРИЯ ПОПОЛНЕНИЙ")

        history = self._stock_service.get_restock_history(
            self._session, supplier_id, limit=100
        )

        if not history:
            print("\n📭 История пополнений пуста")
            print("💡 Пополните товары, чтобы появились записи в истории")
            self._wait()
            return

        print(self._display_service.format_restock_history(history, with_stats=True))

        stats = self._stock_service.get_restock_stats(self._session, supplier_id)
        print(f"\n📊 ОБЩАЯ СТАТИСТИКА ПОПОЛНЕНИЙ:")
        print(f"  📦 Всего пополнений: {stats['total_restocks']}")
        print(f"  📊 Всего товаров пополнено: {stats['total_quantity']} шт.")
        print(f"  📈 Среднее количество: {stats['avg_quantity']:.1f} шт.")

        if history and self._confirm("\n💡 Экспортировать историю в CSV? (y/n): "):
            self._export_to_csv(history)

        self._wait()

    def _export_to_csv(self, history: List) -> None:
        import csv
        from datetime import datetime

        filename = f"restock_history_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"

        try:
            with open(filename, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(['ID', 'Дата', 'Товар', 'Количество', 'Было', 'Стало'])

                for item in history:
                    product_name = item.product.product_name if item.product else "N/A"
                    writer.writerow([
                        item.restock_id,
                        item.restock_date,
                        product_name,
                        item.quantity,
                        item.previous_stock,
                        item.new_stock
                    ])

            print(f"✅ История экспортирована в файл: {filename}")
        except Exception as e:
            print(f"❌ Ошибка при экспорте: {e}")