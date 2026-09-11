from typing import TYPE_CHECKING 

if TYPE_CHECKING:
    from app.domain.entities.warehouse import Warehouse
    from app.domain.entities.node import Node


class TestWarehouse: 
    def test_warehouse_generating(self, warehouse: Warehouse) -> None: 
        # Validate cells count
        assert len(warehouse.cells) == 1800
        
        # Check total amount of aisle
        assert warehouse.cells[-1].aisle == 20
        
        # Chek that each node has 18 cells
        nodes = {node.node_id: 0 for node in warehouse.nodes if node.type_ == "cell_access"}
        for cell in warehouse.cells: 
            nodes[cell.node_id] += 1
            
        for _, cell_count in nodes.items(): 
            assert cell_count == 18
            
        # Check generated node_id on uniqueness
        nodes = []
        for node in warehouse.nodes: 
            if node.type_ != "cell_access": 
                continue
            
            assert node.node_id not in nodes
            nodes.append(node.node_id)
        
        # Check generated cell_id
        for cell in warehouse.cells: 
            aisle, section, side, tier = cell.cell_id.split("-")
            assert cell.aisle == int(aisle[1:])
            assert cell.section == int(section[1:])
            assert cell.tier == int(tier[1:])
            assert cell.side == side
        
        # Check edges
        for edge in warehouse.edges: 
            if (
                "FRONT" not in edge.from_ and 
                "FRON" not in edge.to_ and
                "BACK" not in edge.from_ and
                "BACK" not in edge.to_
            ):
                assert int(edge.from_[1]) < int(edge.to_[1])
            elif "FRONT" in edge.from_ and "FRON" not in edge.to_: 
                assert int(edge.from_.split("-")[0][1:]) == int(edge.to_.split("-")[1][1:])
            elif "BACK" in edge.to_ and "BACK" not in edge.from_:
                assert int(edge.to_.split("-")[0][1:]) == int(edge.from_.split("-")[1][1:]) 
            elif (
                "FRONT" in edge.from_ and "FRONT" in edge.to_ or
                "BACK" in edge.from_ and "BACK" in edge.to_
            ):
                assert int(edge.from_.split("-")[0][1:]) < int(edge.to_.split("-")[0][1:])
                
        # Check weights
        for edge in warehouse.edges: 
            if edge.from_ == "N-DEPOT": 
                continue
            
            from_ = self._find_node_by_id(warehouse, edge.from_)
            to_ = self._find_node_by_id(warehouse, edge.to_)
            
            if (
                "FRONT" in edge.from_ and "FRONT" in edge.to_ or 
                "BACK" in edge.from_ and "BACK" in edge.to_
            ): 
                assert abs(from_.x - to_.x) == edge.weight
            else: 
                assert abs(from_.y - to_.y) == edge.weight

    @staticmethod
    def _find_node_by_id(warehouse: Warehouse, node_id: str) -> Node: 
        for node in warehouse.nodes: 
            if node.node_id == node_id: 
                return node 
    