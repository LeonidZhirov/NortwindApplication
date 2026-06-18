from datetime import date

from cli.customer.handlers import ShowOrdersHandler
from models import Order


class TestShowOrdersHandler:
    def test_handle_with_orders(self, capsys, session, test_customer, test_product):
        handler = ShowOrdersHandler(session)
        handler._wait = lambda: None
        handler._display_header = lambda x: None

        order = Order(
            customer_id=test_customer.customer_id,
            employee_id=1,
            order_date=date.today()
        )
        session.add(order)
        session.flush()

        from models.order_detail_model import OrderDetail
        detail = OrderDetail(
            order_id=order.order_id,
            product_id=test_product.product_id,
            quantity=2,
            unit_price=10.0,
            discount=0
        )
        session.add(detail)
        session.flush()

        handler.handle(customer_id=test_customer.customer_id)

        orders = session.query(Order).filter(
            Order.customer_id == test_customer.customer_id
        ).all()
        assert len(orders) == 1
        assert orders[0].order_id == order.order_id

    def test_handle_no_orders(self, capsys, session, test_customer):
        handler = ShowOrdersHandler(session)
        handler._wait = lambda: None
        handler._display_header = lambda x: None

        session.query(Order).filter(
            Order.customer_id == test_customer.customer_id
        ).delete()
        session.flush()

        handler.handle(customer_id=test_customer.customer_id)

        captured = capsys.readouterr()
        assert "У вас пока нет заказов" in captured.out

    def test_handle_with_shipped_orders(self, capsys, session, test_customer, test_product):
        handler = ShowOrdersHandler(session)
        handler._wait = lambda: None
        handler._display_header = lambda x: None

        order = Order(
            customer_id=test_customer.customer_id,
            employee_id=1,
            order_date=date.today(),
            shipped_date=date.today()
        )
        session.add(order)
        session.flush()

        from models.order_detail_model import OrderDetail
        detail = OrderDetail(
            order_id=order.order_id,
            product_id=test_product.product_id,
            quantity=2,
            unit_price=10.0,
            discount=0
        )
        session.add(detail)
        session.flush()

        handler.handle(customer_id=test_customer.customer_id)

        captured = capsys.readouterr()
        assert str(order.order_id) in captured.out
        assert "Отгружен" in captured.out