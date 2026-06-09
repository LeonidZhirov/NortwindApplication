from sqlalchemy import String, Integer, DateTime
from sqlalchemy.orm import Mapped, mapped_column
from models.base import Base

class Employee(Base):
    __tablename__ = 'employees'

    employee_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    last_name: Mapped[str] = mapped_column(String(20), nullable=False)
    first_name: Mapped[str] = mapped_column(String(10), nullable=False)
    title: Mapped[str] = mapped_column(String(30), nullable=True)
    title_of_courtesy: Mapped[str] = mapped_column(String(25), nullable=True)
    birth_date: Mapped[DateTime] = mapped_column(DateTime, nullable=True)
    hire_date: Mapped[DateTime] = mapped_column(DateTime, nullable=True)
    address: Mapped[str] = mapped_column(String(60), nullable=True)
    city: Mapped[str] = mapped_column(String(15), nullable=True)
    region: Mapped[str] = mapped_column(String(15), nullable=True)
    postal_code: Mapped[str] = mapped_column(String(10), nullable=True)
    country: Mapped[str] = mapped_column(String(15), nullable=True)
    home_phone: Mapped[str] = mapped_column(String(24), nullable=True)
    extension: Mapped[str] = mapped_column(String(4), nullable=True)
    notes: Mapped[str] = mapped_column(String, nullable=True)
    reports_to: Mapped[int] = mapped_column(Integer, nullable=True)

    def __str__(self) -> str:
        return f"{self.first_name} {self.last_name}"