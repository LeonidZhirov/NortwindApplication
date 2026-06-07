from sqlalchemy import text
from sqlalchemy.exc import OperationalError
from db import get_connection

def test_connection():
    try:
        with get_connection() as conn:
            conn.execute(text("SELECT 1"))
            print("✅ Подключение к БД успешно")
            return True

    except OperationalError as e:
        print(f"❌ Ошибка подключения: {e}")
        return False