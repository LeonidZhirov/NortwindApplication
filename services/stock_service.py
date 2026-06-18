# services/stock_service.py
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from datetime import date
from repositories import ProductRepository, StockAlertRepository, RestockHistoryRepository
from models import Product, StockAlert
from models.restock_history_model import RestockHistory


class StockService:
    def __init__(self):
        self.product_repo = ProductRepository()
        self.alert_repo = StockAlertRepository()
        self.restock_history_repo = RestockHistoryRepository()

    def get_low_stock_products(self, session: Session) -> List[Product]:
        return self.product_repo.get_low_stock_products(session)

    def get_out_of_stock_products(self, session: Session) -> List[Product]:
        return self.product_repo.get_out_of_stock_products(session)

    def get_pending_alerts(self, session: Session) -> List[StockAlert]:
        return self.alert_repo.get_pending_alerts(session)

    def get_alerts_by_product(self, session: Session, product_id: int) -> List[StockAlert]:
        return self.alert_repo.get_alerts_by_product(session, product_id)

    def decrease_stock(
        self,
        session: Session,
        product_id: int,
        quantity: int
    ) -> tuple[bool, str, Optional[Product]]:
        if quantity <= 0:
            return False, "Количество должно быть больше 0", None

        stock_info = self.product_repo.get_stock_for_product(session, product_id)
        if stock_info is None:
            return False, "Товар не найден", None

        if stock_info < quantity:
            return False, f"Недостаточно товара. Доступно: {stock_info} шт.", None

        new_quantity = stock_info - quantity
        product = self.product_repo.update_stock(session, product_id, new_quantity)
        if product:
            return True, f"Остаток обновлен: {new_quantity} шт.", product
        return False, "Не удалось обновить остаток", None

    def increase_stock(
        self,
        session: Session,
        product_id: int,
        quantity: int,
        notes: str = None
    ) -> tuple[bool, str, Optional[Product]]:
        if quantity <= 0:
            return False, "Количество должно быть больше 0", None

        current_stock = self.product_repo.get_stock_for_product(session, product_id)
        if current_stock is None:
            return False, "Товар не найден", None

        product = self.product_repo.get_by_id(session, product_id)
        if not product:
            return False, "Товар не найден", None

        new_quantity = current_stock + quantity
        updated = self.product_repo.update_stock(session, product_id, new_quantity)

        if updated:
            self._save_restock_history(
                session=session,
                product_id=product_id,
                supplier_id=product.supplier_id,
                quantity=quantity,
                previous_stock=current_stock,
                new_stock=new_quantity,
                notes=notes
            )
            return True, f"Остаток обновлен: {new_quantity} шт.", updated

        return False, "Не удалось обновить остаток", None

    def resolve_alert(self, session: Session, alert_id: int) -> tuple[bool, str, Optional[StockAlert]]:
        alert = self.alert_repo.get_by_id(session, alert_id)
        if not alert:
            return False, "Уведомление не найдено", None

        product = self.product_repo.get_by_id(session, alert.product_id)
        if not product:
            return False, "Товар не найден", None

        if product.is_low_stock:
            return (
                False,
                f"Нельзя закрыть уведомление: товар '{product.product_name}' "
                f"всё ещё требует пополнения (остаток: {product.units_in_stock or 0}, "
                f"порог: {product.reorder_level or 0})",
                None
            )

        alert.resolve()
        session.flush()
        return True, "Уведомление отмечено как обработанное", alert

    def resolve_all_alerts(self, session: Session) -> tuple[int, List[str]]:
        alerts = self.get_pending_alerts(session)
        resolved_count = 0
        messages = []

        for alert in alerts:
            success, msg, _ = self.resolve_alert(session, alert.alert_id)
            messages.append(msg)
            if success:
                resolved_count += 1

        return resolved_count, messages

    def get_stock_summary(self, session: Session) -> Dict[str, Any]:
        all_products = self.product_repo.get_all(session, limit=1000)
        low_stock = self.get_low_stock_products(session)
        out_of_stock = self.get_out_of_stock_products(session)
        pending_alerts = self.get_pending_alerts(session)

        total_value = sum(
            (p.units_in_stock or 0) * (p.unit_price or 0)
            for p in all_products
        )

        return {
            'total_products': len(all_products),
            'low_stock_count': len(low_stock),
            'out_of_stock_count': len(out_of_stock),
            'pending_alerts_count': len(pending_alerts),
            'total_stock_value': total_value,
            'healthy_products': len(all_products) - len(low_stock)
        }

    def check_product_stock(self, session: Session, product_id: int) -> Optional[Dict[str, Any]]:
        product = self.product_repo.get_by_id(session, product_id)
        if not product:
            return None

        return {
            'product_id': product.product_id,
            'product_name': product.product_name,
            'units_in_stock': product.units_in_stock or 0,
            'reorder_level': product.reorder_level or 0,
            'status': 'low' if product.is_low_stock else 'ok' if product.is_in_stock else 'out',
            'alerts': self.alert_repo.get_alerts_by_product(session, product_id)
        }

    def create_alert_for_product(self, session: Session, product_id: int) -> tuple[bool, str, Optional[StockAlert]]:
        product = self.product_repo.get_by_id(session, product_id)
        if not product:
            return False, "Товар не найден", None

        if product.discontinued:
            return False, "Товар снят с производства", None

        if not product.is_low_stock:
            return False, f"Товар '{product.product_name}' не требует пополнения (остаток: {product.units_in_stock or 0}, порог: {product.reorder_level or 0})", None

        existing_alerts = self.alert_repo.get_alerts_by_product(session, product_id)
        if any(a.status == 'pending' for a in existing_alerts):
            return False, f"Для товара '{product.product_name}' уже есть активное уведомление", None

        alert = StockAlert(
            product_id=product_id,
            current_stock=product.units_in_stock or 0,
            reorder_level=product.reorder_level or 0,
            supplier_id=product.supplier_id,
            status='pending'
        )
        session.add(alert)
        session.flush()

        return True, f"Уведомление создано для товара '{product.product_name}'", alert

    def create_alerts_for_all_low_stock(self, session: Session) -> tuple[int, List[str]]:
        low_stock_products = self.product_repo.get_low_stock_products(session)
        created_count = 0
        messages = []

        for product in low_stock_products:
            success, msg, _ = self.create_alert_for_product(session, product.product_id)
            messages.append(msg)
            if success:
                created_count += 1

        return created_count, messages

    def _save_restock_history(
            self,
            session: Session,
            product_id: int,
            supplier_id: int,
            quantity: int,
            previous_stock: int,
            new_stock: int,
            notes: str = None
    ) -> None:
        history = RestockHistory(
            product_id=product_id,
            supplier_id=supplier_id,
            quantity=quantity,
            previous_stock=previous_stock,
            new_stock=new_stock,
            restock_date=date.today(),
            notes=notes
        )
        session.add(history)
        session.flush()

    def get_restock_history(
            self,
            session: Session,
            supplier_id: int,
            limit: int = 50,
            offset: int = 0
    ) -> List[RestockHistory]:
        return self.restock_history_repo.get_by_supplier(session, supplier_id, limit, offset)

    def get_restock_stats(
            self,
            session: Session,
            supplier_id: int
    ) -> dict:
        return self.restock_history_repo.get_stats_by_supplier(session, supplier_id)