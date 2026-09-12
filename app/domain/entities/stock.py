from dataclasses import dataclass


@dataclass
class Stock: 
    cell_id: str
    product_id: str
    quantity: int
