from services import CartService

class TestCartScenarios:
    def test_add_and_remove_products(self, session, test_customer, test_product):
        cart_service = CartService()

        result = cart_service.add_product(
            session=session,
            customer_id=test_customer.customer_id,
            product_id=test_product.product_id,
            quantity=5
        )
        assert result.success is True

        cart_summary = cart_service.get_cart_summary(session, test_customer.customer_id)
        assert cart_summary['total_quantity'] == 5

        success, message = cart_service.remove_product(
            session=session,
            customer_id=test_customer.customer_id,
            product_id=test_product.product_id,
            quantity=2
        )
        assert success is True
        assert "уменьшено на 2" in message

        cart_summary = cart_service.get_cart_summary(session, test_customer.customer_id)
        assert cart_summary['total_quantity'] == 3

        success, message = cart_service.remove_product(
            session=session,
            customer_id=test_customer.customer_id,
            product_id=test_product.product_id
        )
        assert success is True

        cart_summary = cart_service.get_cart_summary(session, test_customer.customer_id)
        assert cart_summary['is_empty'] is True

    def test_cart_stock_validation(self, session, test_customer, test_product):
        cart_service = CartService()

        cart_service.add_product(
            session=session,
            customer_id=test_customer.customer_id,
            product_id=test_product.product_id,
            quantity=10
        )

        has_stock, issues = cart_service.validate_cart_stock(
            session, test_customer.customer_id
        )
        assert has_stock is True

        test_product.units_in_stock = 5
        session.flush()

        has_stock, issues = cart_service.validate_cart_stock(
            session, test_customer.customer_id
        )
        assert has_stock is False
        assert issues[0]['shortage'] == 5