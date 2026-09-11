import pytest

from app.domain.entities.warehouse import Warehouse


@pytest.fixture(scope="session")
def warehouse() -> Warehouse: 
    return Warehouse()
