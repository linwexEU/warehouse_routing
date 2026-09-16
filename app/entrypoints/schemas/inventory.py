from pydantic import BaseModel, Field

from app.entrypoints.schemas.cart import CartConfig
from app.entrypoints.schemas.pick import SPick


class GenerateWarehouseRequest(BaseModel): 
    aisle_count: int = Field(ge=1, le=20, description="Number of aisles to generate.", examples=[20])
    node_count: int = Field(ge=1, le=5, description="Cell-access nodes per aisle.", examples=[5])


class GenerateWarehouseResponse(BaseModel): 
    nodes: int = Field(description="Total routing nodes generated (depot + junctions + cell-access).", examples=[141])
    cells: int = Field(description="Total storage cells generated (18 per cell-access node).", examples=[1800])
    edges: int = Field(description="Total weighted graph edges.", examples=[159])


class OptimizeRouteRequest(BaseModel): 
    cart: CartConfig | None = Field(default=None, description="Cart caps. Omit to use the randomly generated cart.")
    pick: list[SPick] | None = Field(default=None, description="Pick lines. Omit to use the randomly generated pick list.")


class OptimizeRouteResponse(BaseModel): 
    dropped_nodes: list[str] = Field(description="Access nodes skipped due to cart caps, lowest priority first.", examples=[["N3-A7", "N2-A19"]])
    path_nodes: list[str] = Field(description="Depot-to-depot visit order of access node IDs.", examples=[["N-DEPOT", "N2-A4", "N4-A5"]])
    total_distance: int = Field(description="Total tour length in scaled graph units.", examples=[288])
    total_weight: int = Field(description="Total picked weight in kg.", examples=[28])
    total_volume: int = Field(description="Total picked volume units.", examples=[184])
