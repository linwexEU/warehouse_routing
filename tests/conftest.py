import pytest

from app.domain.entities.warehouse import Warehouse
from app.services.inventory import InventoryService


@pytest.fixture(scope="session")
def warehouse() -> Warehouse: 
    return Warehouse()


@pytest.fixture(scope="session")
def inventory_service(warehouse: warehouse) -> InventoryService: 
    return InventoryService(warehouse)
