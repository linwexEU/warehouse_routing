from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.infrastructure.database.db import InMemoryDb
from app.entrypoints.routers.inventory import router as inventory_router
from app.entrypoints.routers.pages import router as pages_router


@asynccontextmanager
async def lifespan(app: FastAPI): 
    app.state.in_memory_db = InMemoryDb()
    yield


def create_app() -> FastAPI: 
    app = FastAPI(
        lifespan=lifespan,
        title="Warehouse Routing API",
        description=(
            "Portfolio demo: procedurally generated warehouse (aisles/nodes/cells), "
            "graph routing with Dijkstra over aisle junctions, "
            "and single-cart Capacitated VRP order picking solved with Google OR-Tools.\n\n"
            "Typical flow:\n"
            "1. `POST /inventory/generate` — generate a warehouse for your session\n"
            "2. `GET /inventory/cells` — inspect storage cells\n"
            "3. `POST /inventory/optimize` — solve depot-to-depot pick tour with "
            "weight/volume caps and priority-based drops (knapsack tradeoff)"
        ),
        version="0.1.0",
        openapi_tags=[{"name": "Inventory", "description": "Warehouse generation, cell inspection and route optimization."}],
    )
    
    # Register routers
    app.include_router(pages_router)
    app.include_router(inventory_router, prefix="/inventory", tags=["Inventory"])
    
    return app


app = create_app()
