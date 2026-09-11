from typing import TYPE_CHECKING

from app.infrastructure.networkx.graph import NetworkxGraph

if TYPE_CHECKING: 
    from app.domain.entities.warehouse import Warehouse


class TestNetworkxGraph: 
    def test_build_warehouse_graph(self, warehouse: Warehouse) -> None: 
        # Build graph
        warehouse_graph = NetworkxGraph(warehouse)
        warehouse_graph.build_graph()
        
    def test_correct_mapping(self, warehouse: Warehouse) -> None: 
        # Build graph
        warehouse_graph = NetworkxGraph(warehouse)
        warehouse_graph.build_graph()
        
        # Compute dijsktra shortest path
        dijkstra_path_length_only_cell_access, dijkstra_path_only_cell_access = warehouse_graph.compute_dijkstra_path_nodes()
        
        # Map nodes' path and weight to cells
        dijkstra_path_length_cells, dijkstra_path_cells = warehouse_graph.map_dijkstra_path_cells()

        # Check mapped path and weight
        for cell in warehouse.cells: 
            assert dijkstra_path_length_cells[cell.cell_id] == dijkstra_path_length_only_cell_access[cell.node_id]
            assert dijkstra_path_cells[cell.cell_id] == dijkstra_path_only_cell_access[cell.node_id]
