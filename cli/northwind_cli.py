from typing import Dict, Type

from cli.base_role import BaseRole
from cli.customer.role import CustomerRole
from cli.executor.role import ExecutorRole
from cli.supplier.role import SupplierRole
from cli.io_utils import clear_screen, wait_for_key, display_header


class NorthwindCLI:
    def __init__(self):
        self._roles: Dict[str, Type[BaseRole]] = {
            '1': CustomerRole,
            '2': ExecutorRole,
            '3': SupplierRole,
        }

    def clear_screen(self) -> None:
        clear_screen()

    def wait_for_key(self) -> None:
        wait_for_key()

    def display_header(self, title: str) -> None:
        display_header(title)

    def _display_main_menu(self) -> None:
        """Отображение главного меню"""
        print("\n👥 Выберите роль:")
        print("  1. 👤 Покупатель (оформление заказов)")
        print("  2. 👔 Исполнитель (обработка заказов, склад)")
        print("  3. 📦 Поставщик (пополнение склада)")
        print("  0. 🚪 Выход")

    def _display_banner(self) -> None:
        self.clear_screen()
        self.display_header("NORTHWIND SIMULATOR")

        print("\n📦 Симулятор работы организации Northwind")
        print("🏗️ Архитектура: Python + SQLAlchemy ORM + PostgreSQL")
        print("🎨 Паттерны: Strategy, Template Method, Facade, Repository, Service Layer\n")

    def _get_choice(self) -> str:
        return input("\n👉 Ваш выбор: ").strip()

    def _handle_choice(self, choice: str) -> bool:
        if choice == '0':
            print("\n👋 До свидания! Спасибо за использование Northwind Simulator")
            wait_for_key()
            return False

        if choice in self._roles:
            role_class = self._roles[choice]
            role = role_class(self)
            role.run()
            return True

        print("❌ Неверный выбор. Пожалуйста, выберите 0-3")
        wait_for_key()
        return True

    def run(self) -> None:
        while True:
            self._display_banner()
            self._display_main_menu()

            choice = self._get_choice()

            if not self._handle_choice(choice):
                break