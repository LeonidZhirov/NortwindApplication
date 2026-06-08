from decimal import Decimal
from typing import List
from models.cart_item_model import CartItem
from models.order_result_model import OrderResult


class DisplayService:
    @staticmethod
    def clear_screen():
        print("\n" * 2)

    @staticmethod
    def wait_for_key():
        input("\nНажмите Enter для продолжения...")

    @staticmethod
    def display_header(title: str):
        print("\n" + "=" * 80)
        print(f" {title} ".center(80, "="))
        print("=" * 80)

    @staticmethod
    def display_products(products: List):
        if not products:
            print("Товары не найдены")
            return

        print(f"\n{'ID':>3} | {'Название':<40} | {'Цена':>8} | {'Остаток':>5}")
        print("-" * 80)

        for product in products:
            print(product)

        print(f"\n📊 Всего товаров: {len(products)}")

    @staticmethod
    def display_customers(customers: List):
        print("\nДоступные клиенты:")
        print("-" * 80)
        for i, customer in enumerate(customers, 1):
            print(f"{i:>2}. {customer}")

    @staticmethod
    def display_cart(cart_items: List[CartItem]):
        if not cart_items:
            print("\n🛒 Корзина пуста")
            return ''

        print("\n")
        print(f"{'ID':>3} | {'Товар':<40} | {'Цена':>8} | {'Кол-во':>5} | {'Сумма':>10}")
        print("-" * 80)

        total = Decimal('0')
        for item in cart_items:
            print(f"{item.product_id:>3} | {item.product_name:<40} | ${item.unit_price:>8.2f} | {item.quantity:>5} | ${item.total:>10.2f}")
            total += item.total

        print("-" * 80)
        print(f"{'ИТОГО:':>70} ${total:>10.2f}")
        return total

    @staticmethod
    def display_order_summary(result: 'OrderResult'):
        print("\n" + "=" * 80)
        print(" 🎉 ЗАКАЗ УСПЕШНО СОЗДАН! 🎉 ".center(80, "="))
        print("=" * 80)
        print(f"\n  Номер заказа: #{result.order_id}")
        print(f"  Дата заказа: {result.date}")
        print(f"  Сумма заказа: ${result.total:.2f}")
        print(f"\n  Спасибо за покупку, {result.contact_name}!")

    @staticmethod
    def display_error(message: str):
        print(f"\n❌ {message}")

    @staticmethod
    def display_success(message: str):
        print(f"\n✅ {message}")

    @staticmethod
    def display_info(message: str):
        print(f"\nℹ️ {message}")