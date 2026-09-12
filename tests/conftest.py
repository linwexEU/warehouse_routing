import random

import pytest

from app.domain.entities.warehouse import Warehouse
from app.services.inventory import InventoryService
from app.domain.config import settings

random.seed(settings.RANDOM_SEED)


@pytest.fixture(scope="session")
def warehouse() -> Warehouse: 
    return Warehouse()


@pytest.fixture(scope="session")
def inventory_service(warehouse: Warehouse) -> InventoryService: 
    return InventoryService(warehouse)
