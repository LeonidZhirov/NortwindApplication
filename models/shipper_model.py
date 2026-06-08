from sqlalchemy import Integer, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

class Base(DeclarativeBase):
    pass


class Shipper(Base):
    __tablename__ = 'shippers'

    shipper_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    company_name: Mapped[str] = mapped_column(String(40), nullable=False, index=True)

    def __str__(self) -> str:
        return f"{self.shipper_id}: {self.company_name}"