from sqlalchemy import create_engine

DATABASE_URL = "postgresql://postgres:postgres@localhost:55432/northwind"
engine = create_engine(DATABASE_URL, echo=True)

def get_connection():
    return engine.connect()