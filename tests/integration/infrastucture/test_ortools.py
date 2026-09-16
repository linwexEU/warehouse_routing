import random
from typing import TYPE_CHECKING

from app.infrastructure.ortools.solver import ORToolSolver
from app.domain.config import settings

if TYPE_CHECKING: 
    from app.services.inventory import InventoryService
    
random.seed(settings.RANDOM_SEED)


class TestOrToolsSolver: 
    def test_correct_capacity(self, inventory_service: InventoryService) -> None: 
        with ORToolSolver(
            inventory_service.graph, 
            inventory_service.products, 
            inventory_service.stocks,
            inventory_service.pick,
            inventory_service.cart
        ) as solver: 
            solver.solve()
            _, _, _, total_weight_load, total_volume_load = solver.get_solution_info()
            assert total_volume_load <= inventory_service.cart.max_volume
            assert total_weight_load <= inventory_service.cart.max_weight
    