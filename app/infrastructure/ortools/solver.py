import random
from typing import Any, Self

from ortools.constraint_solver import routing_enums_pb2
from ortools.constraint_solver import pywrapcp

from app.infrastructure.networkx.graph import NetworkxGraph
from app.domain.entities.warehouse import Warehouse
from app.domain.entities.pick import Pick
from app.domain.entities.stock import Stock
from app.domain.entities.product import Product
from app.domain.entities.cart import Cart
from app.domain.config import settings
from app.services.inventory import InventoryService

random.seed(settings.RANDOM_SEED)
    
    
class ORToolSolver: 
    def __init__(
        self, 
        graph: NetworkxGraph, 
        products: list[Product], 
        stocks: list[Stock], 
        pick: Pick, 
        cart: Cart
    ) -> None: 
        self.graph = graph
        self.products = products
        self.stocks = stocks
        self.pick = pick
        self.cart = cart
        
        self.data: dict[str, Any] = {}
        self.solution: Any | None = None
        
    def create_data_model(self) -> None: 
        """Create data model for OR-Tool routing"""
        nodes = self.__get_nodes_from_picked_cells()
        
        # Calculate demands weight, demands volume and penalties
        demands_weight = self.__calculate_demands_weight(nodes)
        demands_volume = self.__calculate_demands_volume(nodes)
        penalties = self.__calculate_penalties(nodes)
        
        self.data["penalties"] = penalties
        self.data["nodes"] = ["N-DEPOT"] + list(nodes.keys())
        self.data["distance_matrix"] = self.__build_matrix(nodes)
        self.data["demands_weight"] = demands_weight
        self.data["demands_volume"] = demands_volume
        self.data["vehicle_capacities_weight"] = [self.cart.max_weight]
        self.data["vehicle_capacities_volume"] = [self.cart.max_volume]
        self.data["num_vehicles"] = 1
        self.data["depot"] = 0

    def __get_nodes_from_picked_cells(self) -> dict[str, tuple[str, int, int]]: 
        cells_id = [item[0] for item in self.pick.items]
        nodes = {}
        for cell in self.graph.warehouse.cells: 
            if cell.cell_id not in cells_id: 
                continue
            
            if cell.node_id not in nodes: 
                nodes[cell.node_id] = []
            nodes[cell.node_id].append(self.pick.items[cells_id.index(cell.cell_id)])
        return nodes
    
    def __calculate_demands_weight(self, nodes: dict[str, tuple[str, int, int]]) -> list[int]: 
        demands_weight = [0] 
        for _, pick in nodes.items(): 
            total_weight = 0
            for item in pick:
                stock = self.stocks[item[0]]
                product = self.__find_product_by_product_id(stock.product_id)
                
                total_weight += item[1] * product.weight_per_unit 
            
            demands_weight.append(total_weight)
        return demands_weight
    
    def __calculate_demands_volume(self, nodes: dict[str, tuple[str, int, int]]) -> list[int]: 
        demands_volume = [0]
        for _, pick in nodes.items(): 
            total_weight = 0
            total_volume = 0
            for item in pick:
                stock = self.stocks[item[0]]
                product = self.__find_product_by_product_id(stock.product_id)
                
                total_volume += item[1] * product.volume_per_unit
            
            demands_volume.append(total_volume)
        return demands_volume
    
    def __calculate_penalties(self, nodes: dict[str, tuple[str, int, int]]) -> list[int]: 
        penalties = [0]
        for _, pick in nodes.items(): 
            total_weight = 0
            total_volume = 0
            for item in pick:
                stock = self.stocks[item[0]]
                product = self.__find_product_by_product_id(stock.product_id)
                
                total_weight += item[1] * product.weight_per_unit 
                total_volume += item[1] * product.volume_per_unit
            
            penalties.append(1000 * max(pick, key=lambda x: x[2])[2])
        return penalties
    
    def __find_product_by_product_id(self, product_id: str) -> Product: 
        for product in self.products: 
            if product.product_id == product_id: 
                return product
            
    def __build_matrix(self, nodes: dict[str, tuple[str, int, int]]) -> list[list[int]]: 
        # Create matrix
        matrix = []
        
        # Calculate shortest path for each node, depot first for alignment with demands
        order = ["N-DEPOT"] + list(nodes.keys())
        for source in order: 
            lengths, _ = self.graph.compute_dijkstra_path_nodes(source)
            matrix.append([int(round(lengths[target])) for target in order])
            
        return matrix

    def __init_manager(self) -> None: 
        if not len(self.data): 
            raise ValueError("Data model isn't created!")
        
        self.manager = pywrapcp.RoutingIndexManager(
            len(self.data["distance_matrix"]), self.data["num_vehicles"], self.data["depot"]
        )
        
    def __init_routing(self) -> None: 
        if getattr(self, "manager") is None: 
            raise ValueError("Manager is not initialized!")
        
        self.routing = pywrapcp.RoutingModel(self.manager)
        
    def __register_transit_callback(self) -> None: 
        
        def distance_callback(from_index, to_index):
            """Returns the distance between the two nodes."""
            from_node = self.manager.IndexToNode(from_index)
            to_node = self.manager.IndexToNode(to_index)
            return self.data["distance_matrix"][from_node][to_node]
        
        transit_callback_index = self.routing.RegisterTransitCallback(distance_callback)
        
        # Define a cost for each arc
        self.routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)
        
    def __add_capacity_weight_constraint(self) -> None:
        
        def demands_weight_callback(from_index): 
            from_node = self.manager.IndexToNode(from_index) 
            return self.data["demands_weight"][from_node]
        
        demands_weight_callback_index = self.routing.RegisterUnaryTransitCallback(demands_weight_callback)
        self.routing.AddDimensionWithVehicleCapacity(
            demands_weight_callback_index, 
            0, 
            self.data["vehicle_capacities_weight"], 
            True, 
            "Weight"
        )
        
    def __add_capacity_volume_constraint(self) -> None: 
        
        def demands_volume_callback(from_index): 
            from_node = self.manager.IndexToNode(from_index) 
            return self.data["demands_volume"][from_node]
        
        demands_volume_callback_index = self.routing.RegisterUnaryTransitCallback(demands_volume_callback)
        self.routing.AddDimensionWithVehicleCapacity(
            demands_volume_callback_index, 
            0, 
            self.data["vehicle_capacities_volume"], 
            True, 
            "Volume"
        )
        
    def __add_disjunction(self) -> None: 
        for node in range(1, len(self.data["distance_matrix"])): 
            self.routing.AddDisjunction([self.manager.NodeToIndex(node)], self.data["penalties"][node])

    def __specify_search_parameters(self) -> None: 
        self.search_parameters = pywrapcp.DefaultRoutingSearchParameters()
        self.search_parameters.first_solution_strategy = (
            routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC
        )
        self.search_parameters.local_search_metaheuristic = (
            routing_enums_pb2.LocalSearchMetaheuristic.GUIDED_LOCAL_SEARCH
        )
        self.search_parameters.time_limit.FromSeconds(1)
        
    def solve(self) -> None: 
        if getattr(self, "search_parameters") is None: 
            raise ValueError("Search parameters are not specified")
        self.solution = self.routing.SolveWithParameters(self.search_parameters)
        
    def get_solution_info(self) -> tuple[list[str], list[str], int, int, int]:  # Dropped nodes, total_distance, total_weight_load, total_volume_load
        if self.solution is None: 
            raise ValueError("No solution found!")
        
        dropped_nodes = []
        path_nodes = []
        total_distance = 0
        total_weight_load = 0
        total_volume_load = 0
        
        # Get dropped nodes
        for node in range(self.routing.Size()): 
            if self.routing.IsStart(node) or self.routing.IsEnd(node): 
                continue
            if self.solution.Value(self.routing.NextVar(node)) == node: 
                dropped_nodes.append(self.data["nodes"][node])
                
        # Calculate total_distance, total_weight_load, total_volume_load
        for vehicle_id in range(self.data["num_vehicles"]): 
            if not self.routing.IsVehicleUsed(self.solution, vehicle_id): 
                continue
            
            index = self.routing.Start(vehicle_id)
            route_distance = 0
            route_weight_load = 0
            route_volume_load = 0
            while not self.routing.IsEnd(index): 
                node_index = self.manager.IndexToNode(index)
                path_nodes.append(self.data["nodes"][node_index])
                
                route_weight_load += self.data["demands_weight"][node_index]
                route_volume_load += self.data["demands_volume"][node_index]
                
                prev_index = index
                index = self.solution.Value(self.routing.NextVar(index))
                route_distance += self.routing.GetArcCostForVehicle(
                    prev_index, index, vehicle_id
                )        
            
            total_distance += route_distance
            total_weight_load += route_weight_load
            total_volume_load += route_volume_load
            
        return dropped_nodes, path_nodes, total_distance, total_weight_load, total_volume_load
        
    def __enter__(self) -> Self: 
        self.create_data_model()
        self.__init_manager()
        self.__init_routing()
        self.__register_transit_callback() 
        self.__add_capacity_weight_constraint()
        self.__add_capacity_volume_constraint()
        self.__add_disjunction()
        self.__specify_search_parameters()
        return self
    
    def __exit__(self, exc_type: Any, exc : Any, tb: Any) -> None:
        pass
