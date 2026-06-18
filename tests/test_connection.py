from sqlalchemy import text
from sqlalchemy.exc import OperationalError
from db import SessionLocal

def test_connection_alternative():
    session = SessionLocal()
    try:
        result = session.execute(text("SELECT 1"))
        value = result.scalar()
        print(f"✅ Подключение к БД успешно (результат: {value})")
        session.commit()
        assert True
    except OperationalError as e:
        print(f"❌ Ошибка подключения: {e}")
        session.rollback()
        assert False
    finally:
        session.close()