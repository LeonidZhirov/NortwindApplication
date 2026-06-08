from decimal import Decimal
from sqlalchemy import Integer, ForeignKey, Numeric
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from models.order_dto import  Order


class Base(DeclarativeBase):
    pass


class OrderDetail(Base):
    __tablename__ = 'order_details'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    order_id: Mapped[int] = mapped_column(ForeignKey('orders.id'), nullable=False)
    product_id: Mapped[int] = mapped_column(Integer, nullable=False)
    unit_price: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    discount: Mapped[float] = mapped_column(Numeric(3, 2), nullable=False, default=0.0)

    # Отношение к заказу
    order: Mapped["Order"] = relationship("Order", back_populates="items")

    @property
    def total(self) -> Decimal:
        return self.unit_price * self.quantity * (1 - Decimal(str(self.discount)))