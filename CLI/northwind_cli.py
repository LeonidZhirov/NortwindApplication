from repositories.product_repository import ProductRepository
from repositories.customer_repository import CustomerRepository
from repositories.order_repository import OrderRepository
from repositories.shipper_repository import ShipperRepository
from models.cart_item_model import CartItem
from services.display_service import DisplayService
from ui.input_handler import InputHandler
from services.cart_service import CartService
from services.order_service import OrderService
from models.order_result_model import OrderResult
from typing import List
from db import session
import datetime


class NorthwindCLI:
    def __init__(self):
        self.product_repo = ProductRepository(session)
        self.customer_repo = CustomerRepository(session)
        self.order_repo = OrderRepository(session)
        self.shipper_repo = ShipperRepository(session)

        #self.cart_service = CartService()
        self.carts = {}  # {customer_id: CartService}
        self.order_service = OrderService(self.order_repo)

        self.display = DisplayService()
        self.input_handler = InputHandler(self.product_repo, self.shipper_repo)

        self.current_customer = None

    def run(self):
        while True:
            self.display.clear_screen()
            self.display.display_header("NORTHWIND TRADES")
            self.display.display_info("Добро пожаловать в систему управления заказами")

            print("\nВыберите режим работы:")
            print("  1. 🛍️ Режим покупателя")
            print("  0. 🚪 Выход")

            choice = self.input_handler.get_menu_choice(1)

            if choice == '1':
                self.run_customer_mode()
            elif choice == '0':
                self.display.display_info("До свидания!")
                break
            else:
                self.display.display_error("Неверный выбор")
                self.display.wait_for_key()

    def run_customer_mode(self):
        if not self._select_customer():
            return

        while True:
            cart = self._get_current_cart()
            self.display.clear_screen()
            self.display.display_header("РЕЖИМ ПОКУПАТЕЛЯ")
            self.display.display_info(f"Текущий клиент: {self.current_customer.company_name}")
            self.display.display_info(f"Товаров в корзине: {cart.get_item_count()}")

            print("\nДоступные действия:")
            print("  1. 📋 Просмотреть каталог товаров")
            print("  2. ➕ Добавить товар в корзину")
            print("  3. 🛒 Посмотреть корзину")
            print("  4. 💳 Оформить заказ")
            print("  5. 🔄 Сменить клиента")
            print("  0. 🔙 Вернуться в главное меню")

            choice = self.input_handler.get_menu_choice(5)

            if choice == '1':
                self._show_products()
            elif choice == '2':
                self._add_to_cart()
            elif choice == '3':
                self._show_cart()
            elif choice == '4':
                self._checkout()
            elif choice == '5':
                if self._select_customer():
                    #self.cart_service.clear()
                    pass
            elif choice == '0':
                break
            else:
                self.display.display_error("Неверный выбор")
                self.display.wait_for_key()

    def _get_current_cart(self) -> CartService:
        if self.current_customer is None:
            return None

        customer_id = self.current_customer.customer_id
        if customer_id not in self.carts:
            self.carts[customer_id] = CartService()
        return self.carts[customer_id]

    def _select_customer(self) -> bool:
        self.display.display_header("ВЫБОР КЛИЕНТА")
        customers = self.customer_repo.get_all()

        if not customers:
            self.display.display_error("Клиенты не найдены")
            return False

        self.display.display_customers(customers)

        selected = self.input_handler.select_customer(customers)
        if selected is None:
            return False

        self.current_customer = selected
        self.display.display_success(f"Выбран клиент: {self.current_customer.company_name}")
        self.display.wait_for_key()
        return True

    def _show_products(self):
        products = self.product_repo.get_all()
        self.display.display_header("КАТАЛОГ ТОВАРОВ")
        self.display.display_products(products)
        self.display.wait_for_key()

    def _add_to_cart(self):
        self.display.display_header("ДОБАВЛЕНИЕ ТОВАРА")

        cart = self._get_current_cart()
        products = self.product_repo.get_all()
        self._show_products_preview(products)

        while True:


            product, quantity = self.input_handler.get_product_selection(products)
            if product is None:
                break

            cart_item = CartItem(
                product_id=product.product_id,
                product_name=product.product_name,
                quantity=quantity,
                unit_price=product.unit_price
            )
            cart.add_item(cart_item)
            self.display.display_success(f"Добавлено: {product.product_name} x{quantity} = ${cart_item.total:.2f}")

            if not self.input_handler.ask_continue():
                break

    def _show_products_preview(self, products: List, limit: int = 20):
        print("\nДоступные товары:")
        print("-" * 80)
        for product in products[:limit]:
            print(f"ID: {product.product_id:>3} | {product.product_name:<40} | Цена: ${product.unit_price:>8.2f} | В наличии: {product.units_in_stock}")

        if len(products) > limit:
            print(f"\n... и еще {len(products) - limit} товаров")

    def _show_cart(self):
        self.display.display_header("КОРЗИНА")
        cart = self._get_current_cart()  # добавить
        total = self.display.display_cart(cart.get_items())
        if total:
            self.display.display_info(f"Общая сумма: ${total:.2f}")
        self.display.wait_for_key()

    def _checkout(self):
        cart = self._get_current_cart()
        if cart.is_empty():
            self.display.display_error("Корзина пуста. Невозможно оформить заказ")
            self.display.wait_for_key()
            return False

        self.display.display_header("ОФОРМЛЕНИЕ ЗАКАЗА")
        self._show_cart()

        shippers = list(self.shipper_repo.get_all())
        shipper_id = self.input_handler.select_shipper(shippers)

        self._show_order_details(shippers, shipper_id)

        if not self.input_handler.confirm_action("Подтвердить заказ"):
            self.display.display_error("Заказ отменен")
            self.display.wait_for_key()
            return False

        try:
            result = self._create_order(shipper_id)
            self.display.display_order_summary(result)
            cart.clear()
            self.display.wait_for_key()
            return True

        except Exception as e:
            self.display.display_error(f"Ошибка при создании заказа: {e}")
            self.display.wait_for_key()
            return False

    def _show_order_details(self, shippers: List, shipper_id: int):
        print("\n📋 Детали заказа:")
        print(f"  Клиент: {self.current_customer.company_name}")
        print(f"  Контакт: {self.current_customer.contact_name}")
        shipper_name = next((s.company_name for s in shippers if s.shipper_id == shipper_id), 'Unknown')
        print(f"  Доставка: {shipper_name}")

    def _create_order(self, ship_via: int) -> OrderResult:
        cart = self._get_current_cart()
        order_id = self.order_service.create_order(
            customer_id=self.current_customer.customer_id,
            employee_id=1,
            cart_items=cart.get_items(),
            ship_via=ship_via
        )

        return OrderResult(
            order_id=order_id,
            total=cart.get_total(),
            date=str(datetime.date.today()),
            customer_name=self.current_customer.company_name,
            contact_name=self.current_customer.contact_name
        )