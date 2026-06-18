from sqlalchemy.orm import DeclarativeBase

class Base(DeclarativeBase):
    def __repr__(self) -> str:
        columns = {c.name: getattr(self, c.name) for c in self.__table__.columns}
        return f"<{self.__class__.__name__}({columns})>"