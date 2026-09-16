from dataclasses import dataclass, field
import random

from app.domain.entities.cell import Cell
from app.domain.entities.edge import Edge 
from app.domain.entities.node import Node


@dataclass
class Warehouse: 
    cells: list[Cell] = field(default_factory=list)
    nodes: list[Node] = field(default_factory=list)
    edges: list[Edge] = field(default_factory=list)
    auto: bool = True
    
    def __post_init__(self) -> None: 
        if self.auto:
            self.__generate_warehouse()
            
    def generate_specific_warehouse(self, aisle_count: int, node_count: int) -> None: 
        # Generate the whole warehouse
        self.__generate_nodes(aisle_count, node_count)
        self.__add_edges_between_front_nodes()
        self.__add_edges_between_back_nodes()
        self.__add_depot_node()
        self.__generate_cells()
        
    def __generate_nodes(self, aisle_count: int = 20, node_count: int = 5) -> None: 
        # Start position
        start_x = 1.0
        
        # Generate aisles
        for i in range(aisle_count):      
            self.nodes.append(Node(node_id=f"N{i}-FRONT-JUNCTION", x=start_x, y=0.0, type_="junction"))

            # Start position | Generate nodes
            start_y = 1.0
            for j in range(node_count):
                self.nodes.append(Node(node_id=f"N{j}-A{i}", x=start_x, y=start_y, type_="cell_access"))
                
                # Add Edge with FRONT-JUNCTION
                if j == 0: 
                    self.edges.append(
                        Edge(
                            from_=self.nodes[-2].node_id, 
                            to_=self.nodes[-1].node_id, 
                            weight=self.nodes[-1].y - self.nodes[-2].y,
                            bidirectional=True
                        )
                    )
                else: 
                    # Add Edge between cell nodes
                    self.edges.append(
                        Edge(
                            from_=self.nodes[-2].node_id, 
                            to_=self.nodes[-1].node_id, 
                            weight=self.nodes[-1].y - self.nodes[-2].y,
                            bidirectional=True
                        )
                    )
                
                start_y += random.randint(2, 5)
                
            self.nodes.append(Node(node_id=f"N{i}-BACK-JUNCTION", x=start_x, y=start_y, type_="junction"))
            
            # Add Edge with BACK_JUNCTION
            self.edges.append(
                Edge(
                    from_=self.nodes[-2].node_id, 
                    to_=self.nodes[-1].node_id, 
                    weight=self.nodes[-1].y - self.nodes[-2].y, 
                    bidirectional=True
                )
            )
            
            start_x += random.randint(4, 8)
    
    def __add_edges_between_front_nodes(self) -> None: 
        # Add Edges between all FRONT-NODES and BACK-NODES 
        prev_front_node = None
        for node in self.nodes: 
            if "FRONT" in node.node_id and prev_front_node is None: 
                prev_front_node = node
            elif "FRONT" in node.node_id and prev_front_node: 
                self.edges.append(
                    Edge(from_=prev_front_node.node_id, to_=node.node_id, weight=node.x - prev_front_node.x, bidirectional=True)
                )
                prev_front_node = node
                
    def __add_edges_between_back_nodes(self) -> None: 
        # Add Edges between all BACK-NODES and BACK-NODES 
        prev_back_node = None
        for node in self.nodes: 
            if "BACK" in node.node_id and prev_back_node is None: 
                prev_back_node = node
            elif "BACK" in node.node_id and prev_back_node: 
                self.edges.append(
                    Edge(from_=prev_back_node.node_id, to_=node.node_id, weight=node.x - prev_back_node.x, bidirectional=True)
                )
                prev_back_node = node
                
    def __add_depot_node(self) -> None:
        # Add N-DEPOT
        self.nodes.insert(0, Node(node_id="N-DEPOT", x=0.0, y=0.0, type_="depot"))
        self.edges.append(Edge(from_=self.nodes[0].node_id, to_=self.nodes[1].node_id, weight=1.0, bidirectional=True)) 
        
    def __generate_cells(self, section_count: int = 3, tier_count: int = 3) -> None:
        aisle = 1
        nodes_in_aisle = 0
        for node in self.nodes: 
            if node.type_ != "cell_access": 
                continue
            
            base = (nodes_in_aisle % 5) * section_count
            for section in range(section_count):
                gs = base + section + 1 
                for tier in range(tier_count):
                    for side in ["L", "R"]:
                        self.cells.append(
                            Cell(
                                cell_id=f"A{aisle}-S{gs}-{side}-T{tier + 1}", 
                                zone="A", 
                                aisle=aisle, 
                                side=side, 
                                section=gs, 
                                tier=tier + 1, 
                                node_id=node.node_id
                            )
                        )
                        
            nodes_in_aisle += 1
            if nodes_in_aisle % 5 == 0: 
                aisle += 1
            
    def __generate_warehouse(self) -> None: 
        # Generate the whole warehouse
        self.__generate_nodes()
        self.__add_edges_between_front_nodes()
        self.__add_edges_between_back_nodes()
        self.__add_depot_node()
        self.__generate_cells()
