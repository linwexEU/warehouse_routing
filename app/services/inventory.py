import random
from typing import Any

from fastapi import Request

from app.domain.entities.product import Product 
from app.domain.entities.stock import Stock
from app.domain.entities.cart import Cart
from app.domain.entities.pick import Pick
from app.domain.entities.warehouse import Warehouse 
from app.infrastructure.database.db import InMemoryDb
from app.infrastructure.networkx.graph import NetworkxGraph
from app.infrastructure.ortools.solver import ORToolSolver


class InventoryService: 
    def __init__(
        self, 
        warehouse: Warehouse | None = None, 
        aisle_count: int | None = None, 
        node_count: int | None = None
    ) -> None: 
        if aisle_count and node_count:
            self.warehouse = Warehouse(auto=False)
            self.warehouse.generate_specific_warehouse(aisle_count, node_count)
        else: 
            self.warehouse = Warehouse() if warehouse is None else warehouse
        
        self.graph = NetworkxGraph(self.warehouse)
        
        # Build graph, products, stocks and cart
        self.graph.build()
        self.products = self.__build_products_list()
        self.stocks = self.__build_stocks_list()
        self.cart = self.__build_cart()
        self.pick = self.__generate_pick_items_list()
        
    def add_generated_warehouse(self, db: InMemoryDb, ip_address: str) -> list[int, int, int]: 
        # Add warehouse for user's ip_address
        db.add_generated_warehouse(ip_address, self.warehouse)
        return len(self.warehouse.nodes), len(self.warehouse.cells), len(self.warehouse.edges)
        
    def optimize_route(
        self, 
        max_weight: int | None = None, 
        max_voluem: int | None = None, 
        pick: list[dict[str, Any]] | None = None
    ) -> list[list[str], list[str], int, int, int]:
        # Create cart
        if max_weight and max_voluem:
            self.cart = Cart(
                max_weight=max_weight, 
                max_volume=max_voluem
            )
        
        # Create pick list
        if pick:
            self.pick = Pick(items=[(item["cell_id"], item["quantity"], item["priority"]) for item in pick])
        
        # Get solution
        return self.get_solution()
                    
    def get_solution(self) -> list[list[str], list[str], int, int, int]: 
        with ORToolSolver(
            self.graph, 
            self.products,
            self.stocks,
            self.pick,
            self.cart
        ) as solver:
            solver.solve()
            return solver.get_solution_info()
    
    def __build_products_list(self) -> list[Product]: 
        products = []
        for _ in range(len(self.warehouse.cells)): 
            products.append(Product(
                weight_per_unit=random.randint(1, 5), 
                volume_per_unit=random.randint(10, 30)
            ))
        return products
    
    def __build_stocks_list(self) -> dict[str, Stock]:
        stocks = {}
        for cell, product in zip(self.warehouse.cells, self.products): 
           stocks[cell.cell_id] = Stock(
                cell_id=cell.cell_id,
                product_id=product.product_id,
                quantity=random.randint(1, 5)
            )
        return stocks
    
    def __generate_pick_items_list(self) -> Pick:
        # Prepare cells list
        cells = self.warehouse.cells.copy()
        random.shuffle(cells)
        
        # Generate items
        items = []
        for i in range(random.randint(5, 15)): 
            quantity = self.stocks[cells[i].cell_id].quantity
            items.append((cells[i].cell_id, random.randint(1, quantity), random.randint(1, 3)))
        return Pick(items=items)
    
    @staticmethod
    def __build_cart() -> Cart: 
        return Cart(
            max_weight=random.randint(50, 100),
            max_volume=random.randint(150, 200)
        )
