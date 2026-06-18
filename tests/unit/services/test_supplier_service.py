# tests/unit/services/test_supplier_services.py
from services import StockService, ProductService


class TestStockService:
    def test_create_alert_for_product_success(self, session, test_product):
        service = StockService()
        test_product.units_in_stock = 5
        test_product.reorder_level = 10
        session.flush()

        success, msg, alert = service.create_alert_for_product(
            session, test_product.product_id
        )

        assert success is True
        assert alert is not None
        assert alert.status == 'pending'
        assert alert.current_stock == 5

    def test_create_alert_for_product_insufficient_stock(self, session, test_product):
        service = StockService()
        test_product.units_in_stock = 100
        test_product.reorder_level = 10
        session.flush()

        success, msg, alert = service.create_alert_for_product(
            session, test_product.product_id
        )

        assert success is False
        assert alert is None
        assert "не требует пополнения" in msg

    def test_create_alert_for_duplicate(self, session, test_product):
        service = StockService()
        test_product.units_in_stock = 5
        test_product.reorder_level = 10
        session.flush()

        service.create_alert_for_product(session, test_product.product_id)
        success, msg, alert = service.create_alert_for_product(
            session, test_product.product_id
        )

        assert success is False
        assert "уже есть активное уведомление" in msg

    def test_resolve_alert_success(self, session, test_stock_alert, test_product):
        service = StockService()
        test_product.units_in_stock = 20
        test_product.reorder_level = 10
        session.flush()

        success, msg, alert = service.resolve_alert(
            session, test_stock_alert.alert_id
        )

        assert success is True
        session.refresh(test_stock_alert)
        assert test_stock_alert.status == 'resolved'

    def test_resolve_alert_fails_when_still_low(self, session, test_stock_alert, test_product):
        service = StockService()
        test_product.units_in_stock = 5
        test_product.reorder_level = 10
        session.flush()

        success, msg, alert = service.resolve_alert(
            session, test_stock_alert.alert_id
        )

        assert success is False
        assert "всё ещё требует пополнения" in msg
        session.refresh(test_stock_alert)
        assert test_stock_alert.status == 'pending'


class TestProductService:
    def test_get_products_by_supplier(self, session, test_product, test_supplier):
        service = ProductService()
        test_product.supplier_id = test_supplier.supplier_id
        session.flush()

        products = service.get_products_by_supplier(session, test_supplier.supplier_id)
        assert len(products) == 1
        assert products[0].product_id == test_product.product_id

    def test_get_low_stock_products(self, session):
        from models.product_model import Product
        service = ProductService()

        product1 = Product(
            product_name="Low Stock",
            unit_price=10.0,
            units_in_stock=3,
            reorder_level=10,
            discontinued=0
        )
        product2 = Product(
            product_name="Normal Stock",
            unit_price=15.0,
            units_in_stock=100,
            reorder_level=10,
            discontinued=0
        )
        session.add_all([product1, product2])
        session.flush()

        low_stock = service.get_low_stock_products(session)
        assert len(low_stock) == 1
        assert low_stock[0].product_name == "Low Stock"