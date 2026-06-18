# tests/integration/supplier/test_restock_scenarios.py
from services import StockService, ProductService
from models import Product

class TestRestockScenarios:
    def test_full_restock_workflow(self, session, test_product, test_supplier):
        stock_service = StockService()

        test_product.units_in_stock = 5
        test_product.reorder_level = 10
        test_product.supplier_id = test_supplier.supplier_id
        session.flush()

        success, msg, alert = stock_service.create_alert_for_product(
            session, test_product.product_id
        )
        assert success is True
        assert alert is not None

        alerts = stock_service.get_pending_alerts(session)
        my_alerts = [a for a in alerts if a.supplier_id == test_supplier.supplier_id]
        assert len(my_alerts) == 1

        test_product.units_in_stock = 20
        session.flush()

        success, msg, resolved = stock_service.resolve_alert(
            session, alert.alert_id
        )
        assert success is True
        session.refresh(alert)
        assert alert.status == 'resolved'

    def test_auto_restock_all_alerts(self, session, test_supplier):
        stock_service = StockService()

        products = []
        for i in range(3):
            product = Product(
                product_name=f"Product {i+1}",
                unit_price=10.0 + i,
                units_in_stock=3 + i,
                reorder_level=10,
                supplier_id=test_supplier.supplier_id,
                discontinued=0
            )
            session.add(product)
            session.flush()
            products.append(product)

            stock_service.create_alert_for_product(session, product.product_id)

        alerts = stock_service.get_pending_alerts(session)
        my_alerts = [a for a in alerts if a.supplier_id == test_supplier.supplier_id]
        assert len(my_alerts) == 3

        created_count, messages = stock_service.create_alerts_for_all_low_stock(session)
        assert created_count == 0

        for product in products:
            success, msg, updated = stock_service.increase_stock(
                session, product.product_id, 20
            )
            assert success is True

        resolved_count, messages = stock_service.resolve_all_alerts(session)
        assert resolved_count == 3

    def test_restock_recommendations(self, session, test_supplier):
        product_service = ProductService()
        stock_service = StockService()

        product1 = Product(
            product_name="Out of Stock",
            unit_price=10.0,
            units_in_stock=0,
            reorder_level=10,
            supplier_id=test_supplier.supplier_id,
            discontinued=0
        )
        product2 = Product(
            product_name="Low Stock",
            unit_price=15.0,
            units_in_stock=3,
            reorder_level=10,
            supplier_id=test_supplier.supplier_id,
            discontinued=0
        )
        product3 = Product(
            product_name="Normal Stock",
            unit_price=20.0,
            units_in_stock=100,
            reorder_level=10,
            supplier_id=test_supplier.supplier_id,
            discontinued=0
        )
        session.add_all([product1, product2, product3])
        session.flush()

        stock_service.create_alert_for_product(session, product1.product_id)
        stock_service.create_alert_for_product(session, product2.product_id)

        low_stock = product_service.get_low_stock_products(session)
        assert len(low_stock) == 2

        alerts = stock_service.get_pending_alerts(session)
        my_alerts = [a for a in alerts if a.supplier_id == test_supplier.supplier_id]
        assert len(my_alerts) == 2


class TestRestockHistoryIntegration:
    def test_full_history_workflow(self, session, test_supplier, test_product):
        from services import StockService

        service = StockService()

        success, msg, product = service.increase_stock(
            session, test_product.product_id, 10
        )
        assert success is True

        history = service.get_restock_history(session, test_supplier.supplier_id)
        assert len(history) == 1
        assert history[0].quantity == 10
        assert history[0].previous_stock == 100
        assert history[0].new_stock == 110

        service.increase_stock(session, test_product.product_id, 5)

        stats = service.get_restock_stats(session, test_supplier.supplier_id)
        assert stats['total_restocks'] == 2
        assert stats['total_quantity'] == 15

        from datetime import date, timedelta
        start_date = date.today() - timedelta(days=1)
        end_date = date.today() + timedelta(days=1)

        history_by_date = service.restock_history_repo.get_by_date_range(
            session, test_supplier.supplier_id, start_date, end_date
        )
        assert len(history_by_date) == 2