from typing import TYPE_CHECKING

import networkx as nx
import matplotlib.pyplot as plt

if TYPE_CHECKING: 
    from app.domain.entities.warehouse import Warehouse


class NetworkxGraph: 
    def __init__(self, warehouse: Warehouse) -> None:
        self.graph = nx.Graph()
        self.warehouse = warehouse
        self._dijkstra_cache: dict[str, tuple[dict[str, float], dict[str, list[str]]]] = {}
        
    def build(self) -> nx.Graph: 
        """Build the graph"""
        self.__add_nodes()
        self.__add_edges()
        
        return self.graph
    
    def draw(self) -> None: 
        """Draw the graph"""
        pos = {n.node_id: (n.x, n.y) for n in self.warehouse.nodes}
        
        # Draw nodes, edges, and labels
        nx.draw(self.graph, pos, with_labels=True, node_color='skyblue', node_size=1500, font_size=8, font_weight='bold')
    
        # Draw edge weights as labels
        edge_labels = nx.get_edge_attributes(self.graph, 'weight')
        nx.draw_networkx_edge_labels(self.graph, pos, edge_labels=edge_labels)
        
        # Show graph
        plt.title("Warehouse routing")
        plt.show()
    
    def compute_dijkstra_path_nodes(self, source: str = "N-DEPOT") -> tuple[dict[str, float], dict[str, list[str]]]:
        """Compute dijkstra path, 1x Dijkstra for lengths and paths."""
        dijkstra_path_length, dijkstra_path = self._get_dijkstra(source)
        
        # Get length only for cell_access 
        dijkstra_path_length_routable = {}
        for node, weight in dijkstra_path_length.items(): 
            if "FRONT" in node or "BACK" in node:
                continue
            dijkstra_path_length_routable[node] = weight
        
        # Get path only for cell_access
        dijkstra_path_routable = {}
        for node, path in dijkstra_path.items():
            if "FRONT" in node or "BACK" in node:
                continue 
            dijkstra_path_routable[node] = path
            
        return dijkstra_path_length_routable, dijkstra_path_routable
    
    def _get_dijkstra(self, source: str) -> tuple[dict[str, float], dict[str, list[str]]]:
        """Run single_source_dijkstra once and cache the result."""
        if source not in self._dijkstra_cache:
            self._dijkstra_cache[source] = nx.single_source_dijkstra(self.graph, source=source, weight="weight")
        return self._dijkstra_cache[source]
    
    def map_dijkstra_path_cells(self, source: str = "N-DEPOT") -> tuple[dict[str, float], dict[str, list[str]]]:
        """Map nodes calculation to cells""" 
        dijkstra_path_length_routable, dijkstra_path_routable = self.compute_dijkstra_path_nodes(source)
        
        # Map weight to cells
        dijkstra_path_length_cells = {}   
        for cell in self.warehouse.cells:
            dijkstra_path_length_cells[cell.cell_id] = dijkstra_path_length_routable[cell.node_id]
        
        # Map path to cells 
        dijkstra_path_cells = {}
        for cell in self.warehouse.cells:
            dijkstra_path_cells[cell.cell_id] = dijkstra_path_routable[cell.node_id]
            
        return dijkstra_path_length_cells, dijkstra_path_cells
        
    def __add_nodes(self) -> None: 
        """Add nodes from generated warehouse"""
        for node in self.warehouse.nodes:
            self.graph.add_node(node.node_id)
    
    def __add_edges(self) -> None: 
        """Add edges from generated warehouse"""   
        for edje in self.warehouse.edges: 
            self.graph.add_edge(edje.from_, edje.to_, weight=edje.weight)   
