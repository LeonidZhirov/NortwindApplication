# models/employee_model.py
from typing import List, TYPE_CHECKING
from datetime import date
from sqlalchemy import String, Integer, Date, ForeignKey, Text, LargeBinary
from sqlalchemy.orm import Mapped, mapped_column, relationship
from models.base import Base

if TYPE_CHECKING:
    from models.order_model import Order


class Employee(Base):
    __tablename__ = 'employees'

    employee_id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True
    )
    last_name: Mapped[str] = mapped_column(
        String(20),
        nullable=False
    )
    first_name: Mapped[str] = mapped_column(
        String(10),
        nullable=False
    )
    title: Mapped[str] = mapped_column(
        String(30),
        nullable=True
    )
    title_of_courtesy: Mapped[str] = mapped_column(
        String(25),
        nullable=True
    )
    birth_date: Mapped[date] = mapped_column(
        Date,
        nullable=True
    )
    hire_date: Mapped[date] = mapped_column(
        Date,
        nullable=True
    )
    address: Mapped[str] = mapped_column(
        String(60),
        nullable=True
    )
    city: Mapped[str] = mapped_column(
        String(15),
        nullable=True
    )
    region: Mapped[str] = mapped_column(
        String(15),
        nullable=True
    )
    postal_code: Mapped[str] = mapped_column(
        String(10),
        nullable=True
    )
    country: Mapped[str] = mapped_column(
        String(15),
        nullable=True
    )
    home_phone: Mapped[str] = mapped_column(
        String(24),
        nullable=True
    )
    extension: Mapped[str] = mapped_column(
        String(4),
        nullable=True
    )
    photo: Mapped[bytes] = mapped_column(
        LargeBinary,
        nullable=True
    )
    notes: Mapped[str] = mapped_column(
        Text,
        nullable=True
    )
    reports_to: Mapped[int] = mapped_column(
        Integer,
        ForeignKey('employees.employee_id'),
        nullable=True
    )
    photo_path: Mapped[str] = mapped_column(
        String(255),
        nullable=True
    )

    # Self-referential relationship for hierarchy
    manager: Mapped["Employee"] = relationship(
        "Employee",
        remote_side=[employee_id],
        back_populates="subordinates",
        lazy="selectin"
    )
    subordinates: Mapped[List["Employee"]] = relationship(
        "Employee",
        back_populates="manager",
        lazy="selectin"
    )

    # Relationships
    orders: Mapped[List["Order"]] = relationship(
        "Order",
        back_populates="employee",
        lazy="selectin"
    )

    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}"

    def __str__(self) -> str:
        return f"{self.employee_id:>3} | {self.full_name:<20} | {self.title or 'N/A':<30}"