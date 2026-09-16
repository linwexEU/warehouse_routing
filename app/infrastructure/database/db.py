from app.domain.entities.warehouse import Warehouse


class InMemoryDb: 
    def __init__(self) -> None: 
        self.db = {}
        
    def add_generated_warehouse(self, ip_address: str, warehouse: Warehouse) -> None: 
        self.db[ip_address] = warehouse
    
    def get_warehouse(self, ip_address: str) -> Warehouse | None: 
        return self.db.get(ip_address)
