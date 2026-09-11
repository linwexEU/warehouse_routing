from typing import TYPE_CHECKING 

if TYPE_CHECKING:
    from app.domain.entities.warehouse import Warehouse
    from app.domain.entities.node import Node


class TestWarehouse: 
    def test_counts(self, warehouse: Warehouse) -> None :
        assert len(warehouse.cells) == 1800 
        assert len(warehouse.nodes) == 141
        assert len(warehouse.edges) == 159
        
    def test_cells_per_node(self, warehouse: Warehouse) -> None: 
        nodes = {node.node_id: 0 for node in warehouse.nodes if node.type_ == "cell_access"}
        for cell in warehouse.cells: 
            nodes[cell.node_id] += 1
            
        for _, cell_count in nodes.items(): 
            assert cell_count == 18
    
    def test_check_ids_unique(self, warehouse: Warehouse) -> None: 
        nodes = []
        for node in warehouse.nodes: 
            if node.type_ != "cell_access": 
                continue
            
            assert node.node_id not in nodes
            nodes.append(node.node_id)
            
    def test_cell_id_matches_fields(self, warehouse: Warehouse) -> None: 
        for cell in warehouse.cells: 
            aisle, section, side, tier = cell.cell_id.split("-")
            assert cell.aisle == int(aisle[1:])
            assert cell.section == int(section[1:])
            assert cell.tier == int(tier[1:])
            assert cell.side == side
            
    def test_edge_topology(self, warehouse: Warehouse) -> None: 
        for edge in warehouse.edges: 
            if (
                "FRONT" not in edge.from_ and 
                "FRONT" not in edge.to_ and
                "BACK" not in edge.from_ and
                "BACK" not in edge.to_
            ):
                assert int(edge.from_[1]) < int(edge.to_[1])
            elif "FRONT" in edge.from_ and "FRONT" not in edge.to_: 
                assert int(edge.from_.split("-")[0][1:]) == int(edge.to_.split("-")[1][1:])
            elif "BACK" in edge.to_ and "BACK" not in edge.from_:
                assert int(edge.to_.split("-")[0][1:]) == int(edge.from_.split("-")[1][1:]) 
            elif (
                "FRONT" in edge.from_ and "FRONT" in edge.to_ or
                "BACK" in edge.from_ and "BACK" in edge.to_
            ):
                assert int(edge.from_.split("-")[0][1:]) < int(edge.to_.split("-")[0][1:])
            
            assert edge.weight >= 0
            assert edge.bidirectional == True
            
    def test_edge_weights_match_coords(self, warehouse: Warehouse) -> None: 
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
    