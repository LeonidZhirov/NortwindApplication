from sqlalchemy import String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class Customer(Base):
    __tablename__ = 'customers'

    customer_id: Mapped[str] = mapped_column(String(10), primary_key=True)
    company_name: Mapped[str] = mapped_column(String(40), nullable=False)
    contact_name: Mapped[str] = mapped_column(String(30), nullable=False)

    def __str__(self) -> str:
        return f"{self.customer_id:<10} | {self.company_name:<40} | {self.contact_name:<30}"