# tests/cli/supplier/handlers/test_statistics_handlers.py
from unittest.mock import Mock
from datetime import date
from cli.supplier.handlers import ShowSupplierStatisticsHandler, ShowRestockHistoryHandler, ShowRestockRecommendationsHandler


class TestShowSupplierStatisticsHandler:
    def test_handle_no_products(self, capsys, session, test_supplier):
        from models.product_model import Product
        session.query(Product).filter(
            Product.supplier_id == test_supplier.supplier_id
        ).delete()
        session.flush()

        handler = ShowSupplierStatisticsHandler(session)
        handler._display_header = lambda x: None
        handler._wait = Mock()

        handler.handle(supplier_id=test_supplier.supplier_id)

        captured = capsys.readouterr()
        assert "У поставщика пока нет товаров" in captured.out
        handler._wait.assert_called_once()

    def test_handle_with_products(self, capsys, session, test_supplier, test_product):
        handler = ShowSupplierStatisticsHandler(session)
        handler._display_header = lambda x: None
        handler._wait = Mock()

        handler.handle(supplier_id=test_supplier.supplier_id)

        captured = capsys.readouterr()
        assert "Всего товаров" in captured.out
        assert "Общая стоимость" in captured.out
        handler._wait.assert_called_once()


class TestShowRestockHistoryHandler:
    def test_handle_no_history(self, capsys, session, test_supplier):
        handler = ShowRestockHistoryHandler(session)
        handler._display_header = lambda x: None
        handler._wait = Mock()
        handler._confirm = Mock(return_value=False)

        handler.handle(supplier_id=test_supplier.supplier_id)

        captured = capsys.readouterr()
        assert "История пополнений пуста" in captured.out
        handler._wait.assert_called_once()

    def test_handle_with_history(self, capsys, session, test_supplier, test_product):
        from models.restock_history_model import RestockHistory

        # Создаём записи истории
        history1 = RestockHistory(
            product_id=test_product.product_id,
            supplier_id=test_supplier.supplier_id,
            quantity=10,
            previous_stock=5,
            new_stock=15,
            restock_date=date.today()
        )
        history2 = RestockHistory(
            product_id=test_product.product_id,
            supplier_id=test_supplier.supplier_id,
            quantity=20,
            previous_stock=15,
            new_stock=35,
            restock_date=date.today()
        )
        session.add_all([history1, history2])
        session.flush()

        handler = ShowRestockHistoryHandler(session)
        handler._display_header = lambda x: None
        handler._wait = Mock()
        handler._confirm = Mock(return_value=False)

        handler.handle(supplier_id=test_supplier.supplier_id)

        captured = capsys.readouterr()
        assert "Всего пополнений: 2" in captured.out
        assert "Всего товаров пополнено: 30" in captured.out
        handler._wait.assert_called_once()

    def test_handle_export_csv(self, session, test_supplier, test_product, tmp_path):
        from models.restock_history_model import RestockHistory

        history = RestockHistory(
            product_id=test_product.product_id,
            supplier_id=test_supplier.supplier_id,
            quantity=10,
            previous_stock=5,
            new_stock=15,
            restock_date=date.today()
        )
        session.add(history)
        session.flush()

        handler = ShowRestockHistoryHandler(session)
        handler._display_header = lambda x: None
        handler._wait = Mock()
        handler._confirm = Mock(return_value=True)
        handler._export_to_csv = Mock()

        handler.handle(supplier_id=test_supplier.supplier_id)

        handler._export_to_csv.assert_called_once()
        handler._wait.assert_called_once()

    def test_restock_stats_calculation(self, session, test_supplier, test_product):
        from models.restock_history_model import RestockHistory
        from services import StockService

        history1 = RestockHistory(
            product_id=test_product.product_id,
            supplier_id=test_supplier.supplier_id,
            quantity=10,
            previous_stock=5,
            new_stock=15,
            restock_date=date.today()
        )
        history2 = RestockHistory(
            product_id=test_product.product_id,
            supplier_id=test_supplier.supplier_id,
            quantity=20,
            previous_stock=15,
            new_stock=35,
            restock_date=date.today()
        )
        session.add_all([history1, history2])
        session.flush()

        service = StockService()
        stats = service.get_restock_stats(session, test_supplier.supplier_id)

        assert stats['total_restocks'] == 2
        assert stats['total_quantity'] == 30
        assert stats['avg_quantity'] == 15.0


class TestShowRestockRecommendationsHandler:
    def test_handle_no_recommendations(self, capsys, session, test_supplier, test_product):
        test_product.units_in_stock = 100
        test_product.reorder_level = 10
        session.flush()

        handler = ShowRestockRecommendationsHandler(session)
        handler._display_header = lambda x: None
        handler._wait = Mock()
        handler._confirm = Mock(return_value=False)

        handler.handle(supplier_id=test_supplier.supplier_id)

        captured = capsys.readouterr()
        assert "Все товары в достаточном количестве" in captured.out
        handler._wait.assert_called_once()

    def test_handle_with_recommendations(self, capsys, session, test_supplier, test_product):
        test_product.units_in_stock = 3
        test_product.reorder_level = 10
        session.flush()

        handler = ShowRestockRecommendationsHandler(session)
        handler._display_header = lambda x: None
        handler._wait = Mock()
        handler._confirm = Mock(return_value=False)

        handler.handle(supplier_id=test_supplier.supplier_id)

        captured = capsys.readouterr()
        assert "РЕКОМЕНДАЦИИ ПО ПОПОЛНЕНИЮ" in captured.out
        handler._wait.assert_called_once()

    def test_handle_auto_restock(self, session, test_supplier, test_product):
        test_product.units_in_stock = 3
        test_product.reorder_level = 10
        session.flush()

        handler = ShowRestockRecommendationsHandler(session)
        handler._display_header = lambda x: None
        handler._wait = Mock()
        handler._confirm = Mock(return_value=True)

        handler.handle(supplier_id=test_supplier.supplier_id)

        session.refresh(test_product)
        assert test_product.units_in_stock > 3
        handler._wait.assert_called_once()