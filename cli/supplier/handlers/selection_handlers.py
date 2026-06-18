# cli/supplier/handlers/selection_handlers.py
from typing import Optional

from cli.supplier.handlers.base import BaseSupplierHandler


class SelectSupplierHandler(BaseSupplierHandler):
    def handle(self) -> Optional[int]:
        self._display_header("ВЫБОР ПОСТАВЩИКА")

        suppliers = self._supplier_repo.get_all(self._session)

        if not suppliers:
            print("❌ Поставщики не найдены")
            self._wait()
            return None

        print("\nДоступные поставщики:")
        print("-" * 80)
        for i, supplier in enumerate(suppliers, 1):
            products_count = len(supplier.products) if hasattr(supplier, 'products') else 0
            print(f"{i:>2}. {supplier}")
            print(f"     📦 Товаров: {products_count} | Страна: {supplier.country or 'N/A'}")

        print("\n0. Отмена")

        choice = self._input_choice("\nВыберите поставщика (номер): ", len(suppliers))
        if choice is None or choice == 0:
            return None

        supplier = suppliers[choice - 1]
        print(f"\n✅ Выбран поставщик: {supplier.company_name}")
        print(f"📦 Количество товаров: {len(supplier.products) if hasattr(supplier, 'products') else 0}")
        self._wait()
        return supplier.supplier_id