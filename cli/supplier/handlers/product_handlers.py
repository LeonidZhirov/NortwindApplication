# cli/supplier/handlers/product_handlers.py
from typing import List

from cli.supplier.handlers.base import BaseSupplierHandler
from models import Product


class ShowMyProductsHandler(BaseSupplierHandler):
    def handle(self, supplier_id: int) -> None:
        supplier = self._supplier_repo.get_by_id(self._session, supplier_id)
        supplier_name = supplier.company_name if supplier else "Неизвестный поставщик"

        self._display_header(f"ТОВАРЫ ПОСТАВЩИКА: {supplier_name}")

        products = self._product_service.get_products_by_supplier(self._session, supplier_id)

        if not products:
            print("\n📭 У вас пока нет товаров")
            self._wait()
            return

        active = [p for p in products if not p.discontinued]
        discontinued = [p for p in products if p.discontinued]

        print(f"\n📊 Всего товаров: {len(products)} (активных: {len(active)}, снято: {len(discontinued)})")

        if active:
            print("\n" + "=" * 80)
            print("✅ АКТИВНЫЕ ТОВАРЫ:")
            print(self._display_service.format_products(active, cart_product_ids=None))

        if discontinued:
            print("\n" + "=" * 80)
            print("🚫 СНЯТЫЕ С ПРОИЗВОДСТВА ТОВАРЫ:")
            print(self._display_service.format_products(discontinued, cart_product_ids=None))

        self._display_stock_summary(active)
        self._wait()

    def _display_stock_summary(self, products: List[Product]) -> None:
        total_stock = sum(p.units_in_stock or 0 for p in products)
        total_value = sum(
            (p.units_in_stock or 0) * (p.unit_price or 0)
            for p in products
        )

        print("\n" + "=" * 80)
        print("📊 ОБЩАЯ СТАТИСТИКА:")
        print(f"  📦 Общее количество на складе: {total_stock} шт.")
        print(f"  💰 Общая стоимость: ${float(total_value):,.2f}")


class SearchMyProductsHandler(BaseSupplierHandler):
    """Хендлер: поиск по товарам поставщика."""

    def handle(self, supplier_id: int) -> None:
        query = input("\n🔍 Введите название товара для поиска (или * для всех): ").strip()
        if not query:
            return

        self._display_header(f"ПОИСК: {query}")

        products = self._product_service.get_products_by_supplier(self._session, supplier_id)

        if query == '*':
            found = products
        else:
            found = [p for p in products if query.lower() in p.product_name.lower()]

        if not found:
            print(f"\n❌ Товары по запросу '{query}' не найдены")
        else:
            print(f"\n✅ Найдено товаров: {len(found)}")
            print(self._display_service.format_products(found, cart_product_ids=None))

            low_stock = [p for p in found if p.is_low_stock]
            out_of_stock = [p for p in found if (p.units_in_stock or 0) == 0]

            if low_stock:
                print(f"\n⚠️ Требуют пополнения: {len(low_stock)}")
            if out_of_stock:
                print(f"❌ Нет в наличии: {len(out_of_stock)}")

        self._wait()