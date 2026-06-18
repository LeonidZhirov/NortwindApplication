# cli/__init__.py
from cli.main_cli import NorthwindCLI
from cli.customer.role import CustomerRole
from cli.executor.role import ExecutorRole
from cli.supplier.role import SupplierRole
from cli.base_role import BaseRole

__all__ = [
    'NorthwindCLI',
    'CustomerRole',
    'ExecutorRole',
    'SupplierRole',
    'BaseRole'
]