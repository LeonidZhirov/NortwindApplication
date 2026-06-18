import pytest
from unittest.mock import Mock

from cli.customer.handlers import SelectCustomerHandler


class TestSelectCustomerHandler:
    @pytest.fixture
    def handler(self, session):
        return SelectCustomerHandler(session)

    def test_select_customer_success(self, session, test_customer):
        handler = SelectCustomerHandler(session)

        handler._display_header = Mock()
        handler._wait = Mock()
        handler._input_choice = Mock(return_value=1)

        result = handler.handle()

        assert result == test_customer.customer_id
        handler._display_header.assert_called_once()
        handler._wait.assert_called_once()

    def test_select_customer_cancel(self, session, test_customer):
        handler = SelectCustomerHandler(session)

        handler._display_header = Mock()
        handler._wait = Mock()
        handler._input_choice = Mock(return_value=0)

        result = handler.handle()

        assert result is None
        handler._display_header.assert_called_once()

    def test_select_customer_no_customers(self, session):
        from models.customer_model import Customer
        session.query(Customer).delete()
        session.flush()

        handler = SelectCustomerHandler(session)

        handler._display_header = Mock()
        handler._wait = Mock()
        handler._input_choice = Mock()

        result = handler.handle()

        assert result is None
        handler._display_header.assert_called_once()
        handler._wait.assert_called_once()
        handler._input_choice.assert_not_called()