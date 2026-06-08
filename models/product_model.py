from decimal import Decimal
from sqlalchemy import Integer, String, Numeric, Boolean
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class Product(Base):
    __tablename__ = 'products'

    product_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    product_name: Mapped[str] = mapped_column(String(40), nullable=False, index=True)
    unit_price: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False, default=Decimal("0.00"))
    units_in_stock: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    reorder_level: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    discontinued: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    def __str__(self) -> str:
        return f"{self.product_id:>3} | {self.product_name:<40} | ${self.unit_price:>8.2f} | {self.units_in_stock:>5} шт."