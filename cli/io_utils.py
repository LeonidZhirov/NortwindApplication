# cli/io_utils.py
import subprocess
import sys
from typing import TypeVar, Callable, Optional, Set, List

T = TypeVar('T')


def clear_screen() -> None:
    if sys.platform == "win32":
        subprocess.run("cls", shell=True, check=False)
    else:
        subprocess.run("clear", shell=True, check=False)


def wait_for_key(prompt: str = "Нажмите Enter для продолжения...") -> None:
    input(prompt)


def display_header(title: str, width: int = 80) -> None:
    print("\n" + "=" * width)
    print(f" {title} ".center(width, "="))
    print("=" * width + "\n")


def get_valid_int(
    prompt: str,
    validator: Optional[Callable[[int], bool]] = None,
    default: Optional[int] = None
) -> Optional[int]:
    while True:
        try:
            user_input = input(prompt).strip()
            if not user_input:
                if default is not None:
                    return default
                return None
            val = int(user_input)
            if validator and not validator(val):
                print("❌ Некорректное значение. Попробуйте снова.")
                continue
            return val
        except ValueError:
            print("❌ Введите корректное число")


def get_valid_decimal(
    prompt: str,
    validator: Optional[Callable[[float], bool]] = None,
    default: Optional[float] = None
) -> Optional[float]:
    while True:
        try:
            user_input = input(prompt).strip()
            if not user_input:
                if default is not None:
                    return default
                return None
            val = float(user_input)
            if validator and not validator(val):
                print("❌ Некорректное значение. Попробуйте снова.")
                continue
            return val
        except ValueError:
            print("❌ Введите корректное число (например, 10.99)")


def get_valid_string(
    prompt: str,
    validator: Optional[Callable[[str], bool]] = None,
    default: Optional[str] = None
) -> Optional[str]:
    while True:
        user_input = input(prompt).strip()
        if not user_input:
            if default is not None:
                return default
            return None
        if validator and not validator(user_input):
            print("❌ Некорректное значение. Попробуйте снова.")
            continue
        return user_input


def get_confirmation(prompt: str = "Подтвердить? (y/n): ") -> bool:
    while True:
        user_input = input(prompt).strip().lower()
        if user_input in ('y', 'yes', 'да', 'д'):
            return True
        if user_input in ('n', 'no', 'нет', 'н'):
            return False
        print("❌ Введите 'y' или 'n'")


def parse_id_list(user_input: str, valid_ids: Set[int]) -> List[int]:
    if not user_input:
        return []

    result: Set[int] = set()
    parts = user_input.replace(' ', '').split(',')

    for part in parts:
        if '-' in part:
            try:
                start_str, end_str = part.split('-')
                start, end = int(start_str), int(end_str)
                if start > end:
                    start, end = end, start
                for pid in range(start, end + 1):
                    if pid in valid_ids:
                        result.add(pid)
            except ValueError:
                continue
        else:
            try:
                pid = int(part)
                if pid in valid_ids:
                    result.add(pid)
            except ValueError:
                continue

    return list(result)