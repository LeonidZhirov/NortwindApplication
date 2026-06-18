# cli/base_role.py
from abc import ABC, abstractmethod
from typing import Optional, Dict, Callable

from cli.io_utils import wait_for_key, clear_screen


class BaseRole(ABC):
    def __init__(self, cli_context):
        self.context = cli_context
        self._setup_services()

    def _setup_services(self) -> None:
        pass

    @abstractmethod
    def get_menu_items(self) -> Dict[str, tuple[str, Callable]]:
        """Возвращает словарь {ключ: (описание, функция)}"""
        pass

    @abstractmethod
    def get_role_name(self) -> str:
        """Название роли"""
        pass

    def get_status_info(self) -> Optional[str]:
        """Статусная информация для отображения"""
        return None

    def get_menu_header(self) -> str:
        """Заголовок меню"""
        return f" {self.get_role_name()} ".center(80, "=")

    def _display_menu(self) -> None:
        """Отображение меню"""
        clear_screen()
        print("\n" + "=" * 80)
        print(self.get_menu_header())
        print("=" * 80)

        status = self.get_status_info()
        if status:
            print(f"\n{status}")

        print("\nДоступные действия:")
        for key, (description, _) in self.get_menu_items().items():
            print(f"  {key}. {description}")
        print("  0. 🔙 Вернуться в главное меню")

    def _wait(self) -> None:
        """Ожидание нажатия клавиши"""
        wait_for_key()

    def _execute_action(self, choice: str) -> bool:
        """Выполнить действие"""
        if choice == '0':
            return False

        menu_items = self.get_menu_items()
        if choice in menu_items:
            try:
                menu_items[choice][1]()
                self._wait()
            except ValueError as e:
                print(f"\n❌ Ошибка ввода: {e}")
                self._wait()
            except Exception as e:
                print(f"\n❌ Ошибка: {e}")
                self._wait()
        else:
            print("❌ Неверный выбор")
            self._wait()

        return True

    def run(self) -> None:
        """Основной цикл"""
        while True:
            self._display_menu()
            choice = input("\n👉 Ваш выбор: ").strip()
            if not self._execute_action(choice):
                break