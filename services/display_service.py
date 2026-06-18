# services/display_service.py
from typing import List, Dict, Any

from models import Product, Customer, Order, RestockHistory


class DisplayService:
    @staticmethod
    def format_products(products: List[Product], cart_product_ids: List[int] = None) -> str:
        if not products:
            return "Товары не найдены"

        cart_ids = cart_product_ids or []
        lines = [f"{'ID':>3} | {'Название':<40} | {'Цена':>8} | {'Остаток':>5}"]
        lines.append("-" * 80)

        for product in products:
            marker = "🛒" if product.product_id in cart_ids else " "
            stock_status = "⚠️" if product.is_low_stock else ""
            lines.append(
                f"{marker} {product.product_id:>2} | {product.product_name:<40} | "
                f"${float(product.unit_price or 0):>7.2f} | {(product.units_in_stock or 0):>5} {stock_status}"
            )

        lines.append(f"\n📊 Всего товаров: {len(products)}")
        lines.append("   🛒 - товар в корзине | ⚠️ - низкий остаток")

        return "\n".join(lines)

    @staticmethod
    def format_customers(customers: List[Customer]) -> str:
        if not customers:
            return "Клиенты не найдены"

        lines = [f"{'№':>3} | {'ID':<10} | {'Компания':<40} | {'Контакт':<30}"]
        lines.append("-" * 85)

        for i, customer in enumerate(customers, 1):
            lines.append(
                f"{i:>3} | {customer.customer_id:<10} | "
                f"{customer.company_name[:38]:<40} | {(customer.contact_name or 'N/A')[:28]:<30}"
            )

        return "\n".join(lines)

    @staticmethod
    def format_cart(cart_data: Dict[str, Any]) -> str:
        if cart_data['is_empty']:
            return "🛒 Корзина пуста"

        lines = [f"{'ID':>3} | {'Товар':<40} | {'Цена':>8} | {'Кол-во':>5} | {'Сумма':>10}"]
        lines.append("-" * 80)

        for item in cart_data['items']:
            lines.append(
                f"{item['product_id']:>3} | {item['product_name'][:38]:<40} | "
                f"${float(item['unit_price']):>7.2f} | {item['quantity']:>5} | "
                f"${float(item['total']):>9.2f}"
            )

        lines.append("-" * 80)
        lines.append(f"{'ИТОГО:':>70} ${float(cart_data['total']):>10.2f}")
        lines.append(f"\n📊 Всего позиций: {cart_data['items_count']}, шт: {cart_data['total_quantity']}")

        return "\n".join(lines)

    @staticmethod
    def format_orders(orders: List[Order], with_status: bool = True) -> str:
        if not orders:
            return "Заказы не найдены"

        lines = [f"{'ID':>5} | {'Дата':<12} | {'Клиент':<35} | {'Сумма':>10}"]
        if with_status:
            lines[0] += "| Статус"
            lines.append("-" * 80)
        else:
            lines.append("-" * 65)

        for order in orders:
            total = sum(d.unit_price * d.quantity for d in order.details)
            customer_name = order.customer.company_name if order.customer else 'N/A'

            if with_status:
                status = "✅ Отгружен" if order.is_shipped else "⏳ Ожидает"
                lines.append(
                    f"{order.order_id:>5} | {order.order_date:<12} | "
                    f"{customer_name[:33]:<35} | ${float(total):>9.2f} | {status:<12}"
                )
            else:
                lines.append(
                    f"{order.order_id:>5} | {order.order_date:<12} | "
                    f"{customer_name[:33]:<35} | ${float(total):>9.2f}"
                )

        return "\n".join(lines)

    @staticmethod
    def format_order_details(order_summary: Dict[str, Any]) -> str:
        lines = []

        lines.append(f"📋 Информация о заказе #{order_summary['order_id']}:")
        lines.append(f"  Клиент: {order_summary['customer_name']}")
        lines.append(f"  Контакт: {order_summary['customer_contact']}")
        lines.append(f"  Дата заказа: {order_summary['order_date']}")
        lines.append(f"  Статус: {'✅ Отгружен' if order_summary['is_shipped'] else '⏳ Ожидает отгрузки'}")

        if order_summary.get('shipped_date'):
            lines.append(f"  Дата отгрузки: {order_summary['shipped_date']}")

        lines.append(f"  Доставка: {order_summary['shipper']}")

        lines.append(f"\n{'ID':>3} | {'Товар':<40} | {'Цена':>8} | {'Кол-во':>5} | {'Сумма':>10} | {'Остаток':>8}")
        lines.append("-" * 90)

        for detail in order_summary['details']:
            stock_status = ""
            if detail['current_stock'] < detail['quantity']:
                stock_status = "❌ НЕ ХВАТАЕТ!"
            elif detail['current_stock'] < detail['quantity'] * 2:
                stock_status = "⚠️ МАЛО"

            lines.append(
                f"{detail['product_id']:>3} | {detail['product_name'][:38]:<40} | "
                f"${float(detail['unit_price']):>7.2f} | {detail['quantity']:>5} | "
                f"${float(detail['total']):>9.2f} | {detail['current_stock']:>5} {stock_status}"
            )

        lines.append("-" * 90)
        lines.append(f"{'ИТОГО:':>80} ${float(order_summary['total']):>10.2f}")

        return "\n".join(lines)

    @staticmethod
    def format_alerts(alerts: List[Any]) -> str:
        if not alerts:
            return "✅ Нет активных уведомлений. Все товары в достаточном количестве."

        lines = [f"{'ID':>3} | {'Товар':<40} | {'Поставщик':<30} | {'Остаток':>6} | {'Порог':>5}"]
        lines.append("-" * 95)

        for alert in alerts:
            product_name = alert.product.product_name if alert.product else "N/A"
            supplier_name = alert.supplier.company_name if alert.supplier else "N/A"
            lines.append(
                f"{alert.alert_id:>3} | {product_name[:38]:<40} | "
                f"{supplier_name[:28]:<30} | {alert.current_stock:>5} | "
                f"{alert.reorder_level:>5}"
            )
            lines.append(f"     📅 Создано: {alert.alert_date}")

        return "\n".join(lines)

    @staticmethod
    def format_low_stock_products(products: List[Product]) -> str:
        if not products:
            return "✅ Все товары в достаточном количестве"

        lines = [f"{'ID':>3} | {'Название':<40} | {'Остаток':>8} | {'Порог':>8} | {'Поставщик':<30}"]
        lines.append("-" * 95)

        for product in products:
            supplier_name = product.supplier.company_name if product.supplier else "Не указан"
            lines.append(
                f"{product.product_id:>3} | {product.product_name[:38]:<40} | "
                f"{(product.units_in_stock or 0):>8} | {(product.reorder_level or 0):>8} | "
                f"{supplier_name[:28]:<30}"
            )

        return "\n".join(lines)

    @staticmethod
    def format_statistics(stats: Dict[str, Any]) -> str:
        lines = [
            "📊 Общая статистика:",
            f"  📦 Всего заказов: {stats['total_orders']}",
            f"  ✅ Отгруженных заказов: {stats['shipped_orders']}",
            f"  ⏳ Ожидающих отгрузки: {stats['unshipped_orders']}",
            f"  💰 Общая сумма: ${float(stats['total_amount']):,.2f}",
            f"  📈 Средняя сумма заказа: ${float(stats['average_amount']):,.2f}"
        ]

        return "\n".join(lines)

    @staticmethod
    def format_restock_history(history: List[RestockHistory], with_stats: bool = True) -> str:
        """Форматировать историю пополнений."""
        if not history:
            return "📭 История пополнений пуста"

        lines = [
            f"{'ID':>3} | {'Дата':<12} | {'Товар':<35} | {'Кол-во':>6} | "
            f"{'Было':>6} | {'Стало':>6}"
        ]
        lines.append("-" * 85)

        for item in history:
            product_name = item.product.product_name if item.product else "N/A"
            lines.append(
                f"{item.restock_id:>3} | {item.restock_date:<12} | "
                f"{product_name[:33]:<35} | {item.quantity:>6} | "
                f"{item.previous_stock:>6} | {item.new_stock:>6}"
            )

        if with_stats:
            total_quantity = sum(h.quantity for h in history)
            avg_quantity = total_quantity / len(history) if history else 0
            lines.append("-" * 85)
            lines.append(f"📊 ИТОГО: {len(history)} пополнений, {total_quantity} шт., "
                         f"в среднем {avg_quantity:.1f} шт.")

        return "\n".join(lines)