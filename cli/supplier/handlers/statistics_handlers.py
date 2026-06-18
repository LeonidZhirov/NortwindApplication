# cli/supplier/handlers/statistics_handlers.py
from typing import List, Dict, Any

from cli.supplier.handlers.base import BaseSupplierHandler
from models import Product


class ShowSupplierStatisticsHandler(BaseSupplierHandler):
    def handle(self, supplier_id: int) -> None:
        supplier = self._supplier_repo.get_by_id(self._session, supplier_id)
        supplier_name = supplier.company_name if supplier else "Неизвестный поставщик"

        self._display_header(f"СТАТИСТИКА ПОСТАВЩИКА: {supplier_name}")

        products = self._product_service.get_products_by_supplier(self._session, supplier_id)

        if not products:
            print("\n📭 У поставщика пока нет товаров")
            self._wait()
            return

        stats = self._calculate_statistics(products)
        self._display_statistics(stats)
        self._display_top_products(products)
        self._wait()

    def _calculate_statistics(self, products: List[Product]) -> Dict[str, Any]:
        total = len(products)
        active = len([p for p in products if not p.discontinued])
        discontinued = total - active
        low_stock = len([p for p in products if p.is_low_stock])
        out_of_stock = len([p for p in products if (p.units_in_stock or 0) == 0])

        total_stock = sum(p.units_in_stock or 0 for p in products)
        total_value = sum(
            (p.units_in_stock or 0) * (p.unit_price or 0)
            for p in products
        )

        avg_price = sum(p.unit_price or 0 for p in products) / total if total else 0
        avg_stock = total_stock / total if total else 0

        return {
            'total': total,
            'active': active,
            'discontinued': discontinued,
            'low_stock': low_stock,
            'out_of_stock': out_of_stock,
            'total_stock': total_stock,
            'total_value': total_value,
            'avg_price': avg_price,
            'avg_stock': avg_stock
        }

    def _display_statistics(self, stats: Dict[str, Any]) -> None:
        print(f"\n📊 ОБЩАЯ СТАТИСТИКА:")
        print(f"  📦 Всего товаров: {stats['total']}")
        print(f"  ✅ Активных: {stats['active']}")
        print(f"  🚫 Снятых: {stats['discontinued']}")
        print(f"  ⚠️ Низкий остаток: {stats['low_stock']}")
        print(f"  ❌ Нет в наличии: {stats['out_of_stock']}")

        print(f"\n💰 ФИНАНСОВАЯ СТАТИСТИКА:")
        print(f"  📊 Средняя цена: ${float(stats['avg_price']):.2f}")
        print(f"  📦 Общий остаток: {stats['total_stock']} шт.")
        print(f"  📦 Средний остаток: {float(stats['avg_stock']):.1f} шт.")
        print(f"  💰 Общая стоимость: ${float(stats['total_value']):,.2f}")

    def _display_top_products(self, products: List[Product]) -> None:
        top_expensive = sorted(
            [p for p in products if p.unit_price],
            key=lambda x: x.unit_price,
            reverse=True
        )[:5]

        top_stock = sorted(
            products,
            key=lambda x: x.units_in_stock or 0,
            reverse=True
        )[:5]

        if top_expensive:
            print(f"\n💎 ТОП-5 САМЫХ ДОРОГИХ ТОВАРОВ:")
            for product in top_expensive:
                print(f"  - {product.product_name}: ${float(product.unit_price):.2f}")

        if top_stock:
            print(f"\n📦 ТОП-5 ТОВАРОВ ПО ОСТАТКУ:")
            for product in top_stock:
                print(f"  - {product.product_name}: {product.units_in_stock or 0} шт.")


