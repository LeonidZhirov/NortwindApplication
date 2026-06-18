# services/customer_service.py
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session

from repositories import CustomerRepository
from models import Customer


class CustomerService:
    def __init__(self):
        self.customer_repo = CustomerRepository()

    def get_all_customers(self, session: Session, limit: int = 100, offset: int = 0) -> List[Customer]:
        return self.customer_repo.get_all(session, limit, offset)

    def get_customer(self, session: Session, customer_id: str) -> Optional[Customer]:
        return self.customer_repo.get_by_id(session, customer_id)

    def search_customers(self, session: Session, query: str) -> List[Customer]:
        return self.customer_repo.search(session, query)

    def get_customers_with_orders(self, session: Session, min_orders: int = 1) -> List[Customer]:
        return self.customer_repo.get_customers_with_orders(session, min_orders)

    def get_customers_by_country(self, session: Session, country: str) -> List[Customer]:
        return self.customer_repo.get_customers_by_country(session, country)

    def get_top_customers_by_order_count(self, session: Session, limit: int = 10) -> List[tuple]:
        return self.customer_repo.get_top_customers_by_order_count(session, limit)

    def get_top_customers_by_total(self, session: Session, limit: int = 10) -> List[tuple]:
        return self.customer_repo.get_top_customers_by_total(session, limit)

    def get_customer_summary(self, session: Session, customer_id: str) -> Optional[Dict[str, Any]]:
        customer = self.get_customer(session, customer_id)
        if not customer:
            return None

        return {
            'id': customer.customer_id,
            'company': customer.company_name,
            'contact': customer.contact_name,
            'contact_title': customer.contact_title,
            'city': customer.city,
            'country': customer.country,
            'phone': customer.phone,
            'fax': customer.fax,
            'orders_count': len(customer.orders),
            'total_orders_amount': customer.total_orders_amount
        }

    def get_customers_summary_list(self, session: Session, limit: int = 100) -> List[Dict[str, Any]]:
        customers = self.get_all_customers(session, limit)
        return [
            {
                'id': c.customer_id,
                'company': c.company_name,
                'contact': c.contact_name,
                'city': c.city,
                'country': c.country,
                'orders': len(c.orders)
            }
            for c in customers
        ]