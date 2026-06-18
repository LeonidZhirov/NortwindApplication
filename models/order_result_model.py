from datetime import datetime
from decimal import Decimal
from sqlalchemy import Integer, String, DateTime, Numeric, Text
from sqlalchemy.orm import Mapped, mapped_column
from models.base import Base


class OrderResult(Base):
    __tablename__ = 'order_results'

    result_id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True
    )
    order_id: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        index=True
    )
    operation_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False
    )
    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default='pending'
    )
    total_amount: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        nullable=True
    )
    error_message: Mapped[str] = mapped_column(
        Text,
        nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.now
    )
    processed_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=True
    )
    processed_by: Mapped[int] = mapped_column(
        Integer,
        nullable=True
    )

    @property
    def is_success(self) -> bool:
        return self.status == 'success'

    @property
    def is_failed(self) -> bool:
        return self.status == 'failed'

    def __str__(self) -> str:
        status_icon = "✅" if self.is_success else "❌" if self.is_failed else "⏳"
        return f"{status_icon} OrderResult #{self.result_id} | Order #{self.order_id} | {self.operation_type} | {self.status}"