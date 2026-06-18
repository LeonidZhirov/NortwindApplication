# services/order_service.py
from typing import List, Optional, Dict, Any
from decimal import Decimal
from datetime import date, timedelta
from sqlalchemy.orm import Session

from repositories import OrderRepository, ProductRepository, StockAlertRepository, CartRepository, ShipperRepository
from models import Order, OrderDetail, StockAlert, Shipper
from .stock_manager import StockManager, InsufficientStockError


class OrderService:
    def __init__(self):
        self.order_repo = OrderRepository()
        self.product_repo = ProductRepository()
        self.stock_alert_repo = StockAlertRepository()
        self.shipper_repo = ShipperRepository()
        self.cart_repo = CartRepository()
        self.stock_manager = StockManager()


    def create_order_from_cart(
            self,
            session: Session,
            customer_id: str,
            cart_items: List[Dict[str, Any]],
            employee_id: int = 1,
            shipper_id: int = 1
    ) -> Order:
        for item in cart_items:
            product = self.product_repo.get_by_id(session, item['product_id'])
            if not product:
                raise ValueError(f"Товар #{item['product_id']} не найден")

            if (product.units_in_stock or 0) < item['quantity']:
                raise InsufficientStockError(
                    product_id=product.product_id,
                    product_name=product.product_name,
                    required=item['quantity'],
                    available=product.units_in_stock or 0
                )

        order = Order(
            order_id=Order.generate_next_id(session),
            customer_id=customer_id,
            employee_id=employee_id,
            order_date=date.today(),
            ship_via=shipper_id
        )
        session.add(order)
        session.flush()

        order_details = []
        for item in cart_items:
            order_detail = OrderDetail(
                order_id=order.order_id,
                product_id=item['product_id'],
                unit_price=item['unit_price'],
                quantity=item['quantity'],
                discount=0
            )
            session.add(order_detail)
            order_details.append(order_detail)

        self.cart_repo.clear_cart(session, customer_id)

        session.flush()
        session.refresh(order)

        return order

    def get_order(self, session: Session, order_id: int) -> Optional[Order]:
        return self.order_repo.get_by_id(session, order_id)

    def get_order_with_details(self, session: Session, order_id: int) -> Optional[Order]:
        return self.order_repo.get_order_with_details(session, order_id)

    def get_customer_orders(self, session: Session, customer_id: str) -> List[Order]:
        return self.order_repo.get_orders_by_customer(session, customer_id)

    def get_unshipped_orders(self, session: Session) -> List[Order]:
        return self.order_repo.get_unshipped_orders(session)

    def get_shipped_orders(self, session: Session, limit: int = 50) -> List[Order]:
        return self.order_repo.get_shipped_orders(session, limit)

    def get_recent_orders(self, session: Session, days: int = 7) -> List[Order]:
        since_date = date.today() - timedelta(days=days)
        return self.order_repo.get_orders_by_date_range(session, since_date, date.today())

    def validate_order_shippable(
            self,
            session: Session,
            order_id: int
    ) -> tuple[bool, List[Dict]]:
        order = self.get_order_with_details(session, order_id)
        if not order:
            return False, [{'error': f'Заказ #{order_id} не найден'}]

        if order.is_shipped:
            return False, [{'error': f'Заказ #{order_id} уже отгружен'}]

        issues = []
        for detail in order.details:
            if (detail.product.units_in_stock or 0) < detail.quantity:
                issues.append({
                    'product_id': detail.product_id,
                    'product_name': detail.product.product_name,
                    'required': detail.quantity,
                    'available': detail.product.units_in_stock or 0,
                    'shortage': detail.quantity - (detail.product.units_in_stock or 0)
                })

        return len(issues) == 0, issues

    def ship_order(self, session: Session, order_id: int, employee_id: int = 1) -> Order:
        can_ship, issues = self.validate_order_shippable(session, order_id)
        if not can_ship:
            if issues and 'error' in issues[0]:
                raise ValueError(issues[0]['error'])
            raise ValueError(f"Невозможно отгрузить заказ: {issues}")

        order = self.order_repo.get_order_for_shipping(session, order_id)
        if not order:
            raise ValueError(f"Заказ #{order_id} не найден")

        alerts = []

        for detail in order.details:
            product = self.product_repo.update_stock(
                session,
                detail.product_id,
                (detail.product.units_in_stock or 0) - detail.quantity
            )
            if not product:
                raise ValueError(f"Товар #{detail.product_id} не найден")

            if product.is_low_stock:
                alerts.append({
                    'product': product,
                    'current_stock': product.units_in_stock,
                    'reorder_level': product.reorder_level or 0,
                    'supplier_id': product.supplier_id
                })

        order = self.order_repo.update_shipped_date(session, order_id, date.today())
        order.employee_id = employee_id
        if not order:
            raise ValueError(f"Не удалось обновить дату отгрузки для заказа #{order_id}")

        for alert_data in alerts:
            if alert_data['supplier_id']:
                alert = StockAlert(
                    product_id=alert_data['product'].product_id,
                    current_stock=alert_data['current_stock'] or 0,
                    reorder_level=alert_data['reorder_level'],
                    supplier_id=alert_data['supplier_id'],
                    status='pending'
                )
                self.stock_alert_repo.add_alert(session, alert)

        session.flush()
        return order

    def get_order_summary(self, session: Session, order_id: int) -> Optional[Dict[str, Any]]:
        order = self.get_order_with_details(session, order_id)
        if not order:
            return None

        details = []
        total = Decimal('0')

        for detail in order.details:
            total += detail.total
            details.append({
                'product_id': detail.product_id,
                'product_name': detail.product.product_name,
                'unit_price': detail.unit_price,
                'quantity': detail.quantity,
                'discount': detail.discount,
                'total': detail.total,
                'current_stock': detail.product.units_in_stock or 0
            })

        return {
            'order_id': order.order_id,
            'customer_id': order.customer_id,
            'customer_name': order.customer.company_name if order.customer else 'N/A',
            'customer_contact': order.customer.contact_name if order.customer else 'N/A',
            'order_date': order.order_date,
            'shipped_date': order.shipped_date,
            'is_shipped': order.is_shipped,
            'shipper': order.shipper.company_name if order.shipper else 'N/A',
            'details': details,
            'items_count': len(details),
            'total_quantity': sum(d['quantity'] for d in details),
            'total': total
        }

    def get_statistics(self, session: Session) -> Dict[str, Any]:
        return {
            'total_orders': self.order_repo.get_total_orders_count(session),
            'shipped_orders': self.order_repo.get_shipped_orders_count(session),
            'unshipped_orders': self.order_repo.get_unshipped_orders_count(session),
            'total_amount': self.order_repo.get_total_amount_sum(session),
            'average_amount': self.order_repo.get_average_order_amount(session)
        }

    def get_shippers(self, session: Session) -> List[Shipper]:
        return self.shipper_repo.get_all(session)

    def get_default_shipper(self, session: Session) -> Shipper:
        return self.shipper_repo.get_default_shipper(session)

    def cancel_order(self, session: Session, order_id: int) -> bool:
        order = self.get_order_with_details(session, order_id)

        if not order:
            raise ValueError(f"Заказ #{order_id} не найден")

        if order.is_shipped:
            raise ValueError(f"Нельзя отменить уже отгруженный заказ #{order_id}")

        session.delete(order)
        session.flush()

        return True