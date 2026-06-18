from services import CartService, OrderService


class TestPurchaseScenario:
    def test_full_purchase_flow(self, session, test_customer, test_product):
        cart_service = CartService()
        order_service = OrderService()

        result = cart_service.add_product(
            session=session,
            customer_id=test_customer.customer_id,
            product_id=test_product.product_id,
            quantity=3
        )
        assert result.success is True

        cart_summary = cart_service.get_cart_summary(session, test_customer.customer_id)
        assert cart_summary['items_count'] == 1
        assert cart_summary['total_quantity'] == 3

        order = order_service.create_order_from_cart(
            session=session,
            customer_id=test_customer.customer_id,
            cart_items=[{'product_id': test_product.product_id, 'quantity': 3, 'unit_price': 10.0}],
            employee_id=1,
            shipper_id=1
        )

        session.refresh(test_product)
        assert test_product.units_in_stock == 100

        order_service.ship_order(session, order.order_id)
        session.refresh(test_product)
        assert test_product.units_in_stock == 97