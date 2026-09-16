import asyncio

from fastapi import APIRouter, Request, HTTPException, status

from app.entrypoints.schemas.cell import CellsInfo
from app.entrypoints.schemas.inventory import (
    GenerateWarehouseRequest, 
    GenerateWarehouseResponse, 
    OptimizeRouteRequest, 
    OptimizeRouteResponse
)
from app.services.inventory import InventoryService

router = APIRouter()


@router.post(
    "/generate",
    summary="Generate warehouse",
    description="Procedurally generate aisles, routing nodes/edges and storage cells for your session (keyed by client IP). Resets previous session data.",
    response_description="Counts of generated topology.",
    status_code=status.HTTP_200_OK,
    responses={422: {"description": "aisle_count 1-20 / node_count 1-5 validation failed."}},
)
async def generate_warehouse(request: Request, payload: GenerateWarehouseRequest) -> GenerateWarehouseResponse: 
    service = InventoryService(aisle_count=payload.aisle_count, node_count=payload.node_count)
    response = await asyncio.to_thread(
        service.add_generated_warehouse, 
        request.app.state["in_memory_db"], 
        request.client.host
    )
    return GenerateWarehouseResponse(
        nodes=response[0], 
        cells=response[1], 
        edges=response[2]
    )


@router.get(
    "/cells",
    summary="List storage cells",
    description="Returns all storage cells of your generated warehouse (18 per cell-access node). Generate first — 404 otherwise.",
    response_description="Cell catalog with routing access nodes.",
    responses={404: {"description": "No warehouse generated for this session yet."}},
)
async def get_cells(request: Request) -> CellsInfo: 
    warehouse = request.app.state["in_memory_db"].get_warehouse(request.client.host)
    
    if warehouse is not None:
        return CellsInfo.from_entity(warehouse.cells)
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="You don't have generated warehouse!")


@router.post(
    "/optimize",
    summary="Optimize pick route (CVRP)",
    description=(
        "Solve single-cart Capacitated VRP with OR-Tools over Dijkstra pick-to-pick distances: "
        "depot-to-depot tour, weight + volume caps, priority-based drops (1=low drops first). "
        "Omit cart/pick to use the generated defaults. Requires a generated warehouse — 404 otherwise."
    ),
    response_description="Visit order of access node IDs, dropped nodes, and tour totals.",
    responses={
        404: {"description": "No warehouse generated for this session yet."},
        422: {"description": "Unknown cell_id, quantity over stock, or invalid cart/priority."},
    },
)
async def optimize_route(request: Request, payload: OptimizeRouteRequest) -> OptimizeRouteResponse: 
    warehouse = request.app.state["in_memory_db"].get_warehouse(request.client.host)
    if warehouse is None: 
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="You don't have generated warehouse!")
    
    service = InventoryService(warehouse)
    response = await asyncio.to_thread(
        service.optimize_route, 
        payload.cart.max_weight if payload.cart else None, 
        payload.cart.max_volume if payload.cart else None, 
        [item.model_dump() for item in payload.pick] if payload.pick else None
    )
    return OptimizeRouteResponse(
        dropped_nodes=response[0], 
        path_nodes=response[1], 
        total_distance=response[2], 
        total_weight=response[3],
        total_volume=response[4]
    )
    