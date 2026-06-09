from decimal import Decimal
from sqlalchemy import Integer, Numeric, String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from models.base import Base


class OrderResult(Base):
    __tablename__ = 'order_results'

    order_result_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    order_id: Mapped[int] = mapped_column(Integer, ForeignKey('orders.order_id'), nullable=False, unique=True, index=True)
    total: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    date: Mapped[str] = mapped_column(String(20), nullable=False) 
    customer_name: Mapped[str] = mapped_column(String(100), nullable=False)
    contact_name: Mapped[str] = mapped_column(String(100), nullable=False)

    def __str__(self) -> str:
        return f"Order #{self.order_id} | {self.customer_name} | {self.date} | {self.total}"