import pytest
from sqlalchemy import create_engine, text

DATABASE_URL = "postgresql://postgres:postgres@localhost:55432/northwind"

def test_connection():
    engine = create_engine(DATABASE_URL)
    with engine.connect() as conn:
        result = conn.execute(text("SELECT 1"))
        assert result.fetchone()[0] == 1

def test_tables_exist():
    engine = create_engine(DATABASE_URL)
    with engine.connect() as conn:
        result = conn.execute(text("""
            SELECT COUNT(*) 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
        """))
        assert result.fetchone()[0] > 0