import random
from typing import TYPE_CHECKING

from app.services.inventory import InventoryService
from app.domain.config import settings

random.seed(settings.RANDOM_SEED)

if TYPE_CHECKING: 
    from app.services.inventory import InventoryService


class TestInventoryService: 
    def test_build_successfully(self, inventory_service: InventoryService) -> None:
        assert inventory_service.warehouse is not None 
        assert inventory_service.pick is not None
        assert inventory_service.cart is not None
        assert len(inventory_service.products) >= 1
        assert len(inventory_service.stocks) >= 1
    
    def test_generated_products_list(self, inventory_service: InventoryService) -> None: 
        assert len(inventory_service.products) == len(inventory_service.warehouse.cells)
        
    def test_generated_stocks(self, inventory_service: InventoryService) -> None: 
        assert len(inventory_service.stocks) == len(inventory_service.warehouse.cells) 
    
    def test_generated_pick_items(self, inventory_service: InventoryService) -> None: 
        for pick_item in inventory_service.pick.items: 
            cell_id, quantity, _ = pick_item
            assert quantity <= inventory_service.stocks[cell_id].quantity
