from sqlalchemy import create_engine, text
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


'''def test_tables_exist():
    with engine.connect() as conn:
        result = conn.execute(text("""
            SELECT COUNT(*) 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
        """))
        assert result.fetchone()[0] > 0'''