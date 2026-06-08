from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import select
from models.customer_model import Customer


class CustomerRepository:
    def __init__(self, session: Session):
        self.session = session

    def get_all(self) -> List[Customer]:
        return list(self.session.execute(
            select(Customer).order_by(Customer.company_name)
        ).scalars().all())

    def get_by_id(self, customer_id: str) -> Optional[Customer]:
        return self.session.get(Customer, customer_id)