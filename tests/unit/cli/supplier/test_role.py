# tests/cli/supplier/test_role.py
import pytest
from unittest.mock import Mock, patch

from cli.supplier.role import SupplierRole


class TestSupplierRole:
    @pytest.fixture
    def mock_cli_context(self):
        context = Mock()
        context.clear_screen = Mock()
        context.wait_for_key = Mock()
        context.display_header = Mock()
        return context

    def test_get_role_name(self, mock_cli_context):
        role = SupplierRole(mock_cli_context)
        assert "ПОСТАВЩИКА" in role.get_role_name()

    def test_get_menu_items(self, mock_cli_context):
        role = SupplierRole(mock_cli_context)
        menu = role.get_menu_items()
        expected_keys = ['1', '2', '3', '4', '5', '6', '7', '8']
        for key in expected_keys:
            assert key in menu

    def test_get_status_info_no_supplier(self, mock_cli_context):
        role = SupplierRole(mock_cli_context)
        status = role.get_status_info()
        assert "Поставщик не выбран" in status

    def test_get_status_info_with_supplier(self, session, test_supplier, test_product):
        mock_context = Mock()
        role = SupplierRole(mock_context)
        role._supplier_id = test_supplier.supplier_id

        with patch.object(role._session_manager, 'session') as mock_session:
            mock_session.return_value.__enter__.return_value = session
            status = role.get_status_info()

            assert test_supplier.company_name in status
            assert "Всего товаров: 1" in status

    def test_require_supplier_true(self, mock_cli_context):
        role = SupplierRole(mock_cli_context)
        role._supplier_id = 1
        assert role._require_supplier() is True

    def test_require_supplier_false(self, mock_cli_context):
        role = SupplierRole(mock_cli_context)
        role._supplier_id = None
        role._wait = Mock()
        assert role._require_supplier() is False
        role._wait.assert_called_once()

    @patch('cli.supplier.role.SelectSupplierHandler')
    def test_select_supplier(self, mock_handler, mock_cli_context):
        role = SupplierRole(mock_cli_context)
        mock_handler.return_value.handle.return_value = 1

        with patch.object(role._session_manager, 'session'):
            role._select_supplier()

        assert role._supplier_id == 1

    @patch('builtins.input')
    def test_run_with_supplier_selected(self, mock_input, mock_cli_context):
        role = SupplierRole(mock_cli_context)
        role._select_supplier = Mock()
        role._supplier_id = 1
        role._display_menu = Mock()
        role._execute_action = Mock(return_value=False)
        mock_input.return_value = "0"

        role.run()

        role._select_supplier.assert_called_once()
        role._display_menu.assert_called()

    @patch('builtins.input')
    def test_run_with_no_supplier(self, mock_input, mock_cli_context):
        role = SupplierRole(mock_cli_context)
        role._select_supplier = Mock()
        role._supplier_id = None

        role.run()

        role._select_supplier.assert_called_once()
        # super().run() не вызывается, т.к. supplier_id = None