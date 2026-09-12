import random

from app.domain.entities.product import Product 
from app.domain.entities.stock import Stock
from app.domain.entities.cart import Cart
from app.domain.entities.pick import Pick
from app.domain.entities.warehouse import Warehouse 
from app.infrastructure.networkx.graph import NetworkxGraph


class InventoryService: 
    def __init__(self) -> None: 
        self.warehouse = Warehouse()
        self.graph = NetworkxGraph(self.warehouse)
        
        # Build graph, products, stocks and cart
        self.graph.build()
        self.products = self.__build_products_list()
        self.stocks = self.__build_stocks_list()
        self.cart = self.__build_cart()
        self.pick_items = self.__generate_pick_items_list()
    
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
