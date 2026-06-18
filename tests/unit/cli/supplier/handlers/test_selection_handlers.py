# tests/cli/supplier/handlers/test_selection_handlers.py
from unittest.mock import Mock

from cli.supplier.handlers import SelectSupplierHandler


class TestSelectSupplierHandler:
    def test_select_supplier_success(self, session, test_supplier):
        handler = SelectSupplierHandler(session)
        handler._display_header = lambda x: None
        handler._wait = Mock()
        handler._input_choice = Mock(return_value=1)

        result = handler.handle()

        assert result == test_supplier.supplier_id
        handler._wait.assert_called_once()

    def test_select_supplier_cancel(self, session, test_supplier):
        handler = SelectSupplierHandler(session)
        handler._display_header = lambda x: None
        handler._wait = Mock()
        handler._input_choice = Mock(return_value=0)

        result = handler.handle()

        assert result is None
        handler._wait.assert_not_called()

    def test_select_supplier_no_suppliers(self, session):
        from models.supplier_model import Supplier
        session.query(Supplier).delete()
        session.flush()

        handler = SelectSupplierHandler(session)
        handler._display_header = lambda x: None
        handler._wait = Mock()
        handler._input_choice = Mock()

        result = handler.handle()

        assert result is None
        handler._wait.assert_called_once()
        handler._input_choice.assert_not_called()