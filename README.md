# Warehouse Order-Picking Route Optimizer

Single-cart Capacitated VRP demo: generate a synthetic warehouse, route it as a graph
with Dijkstra, and solve order picking with Google OR-Tools — via REST API plus a
minimal browser front-end.

## What it does

1. **Generates a warehouse** — aisles, routing nodes (`depot` / `junction` /
   `cell_access`), weighted edges, and storage cells (18 cells share one access node).
2. **Routes on a graph** — topology loaded into NetworkX; pick-to-pick distances come
   from Dijkstra shortest paths (junctions are transit only, never stops).
3. **Optimizes the pick tour** — single-cart CVRP with weight + volume caps. If the
   pick list doesn't fit, low-priority picks are dropped first (knapsack-style
   tradeoff via OR-Tools disjunction penalties). Result is a depot-to-depot visit
   order with totals.

## Stack

Python ≥3.14, FastAPI + Jinja2 front-end, NetworkX, OR-Tools, Pydantic Settings,
pytest. Managed with `uv`.

## Setup

```bash
uv sync
cp app/.env-example app/.env   # then set a value, e.g. RANDOM_SEED=1
```

`RANDOM_SEED` is required — it seeds warehouse topology and the demo
products/stocks/picks/carts.

## Run

```bash
uv run uvicorn app.main:app --reload
```

- Front-end: `GET /` — generate, browse cells (paginated), optimize.
- Swagger: `GET /docs`

## API

Session state (generated warehouse) is kept in an in-memory DB keyed by client IP.

| Method | Endpoint | Purpose |
|---|---|---|
| `POST` | `/inventory/generate` | Generate warehouse (`aisle_count` 1–20, `node_count` 1–5). Resets session. |
| `GET` | `/inventory/cells?limit=50&offset=0` | Paginated cells (`total/limit/offset` + page). 404 before generate. |
| `POST` | `/inventory/optimize` | Solve tour. Optional `cart` + `pick`; omitted = generated defaults. |

Generate:

```json
POST /inventory/generate
{ "aisle_count": 5, "node_count": 3 }
```

Optimize (all fields optional):

```json
POST /inventory/optimize
{
  "cart": { "max_weight": 78, "max_volume": 189 },
  "pick": [
    { "cell_id": "A18-S11-R-T3", "quantity": 1, "priority": 3 }
  ]
}
```

Response:

```json
{
  "dropped_nodes": ["N3-A7"],
  "path_nodes": ["N-DEPOT", "N2-A4", "N4-A5"],
  "total_distance": 288,
  "total_weight": 28,
  "total_volume": 184
}
```

Rules: `quantity` must not exceed stock in the cell; `priority` 1 (drops first) to 3
(kept); each matrix index maps to `nodes[i]` (index 0 is `N-DEPOT`); distances are
scaled integers for OR-Tools.

## How it works

- `app/domain/entities/` — pure dataclasses: `Warehouse`, `Cell`, `Node`, `Edge`,
  `Product`, `Stock`, `Pick`, `Cart`. No I/O.
- `app/services/inventory.py` — builds demo products/stocks/cart/picks, maps pick
  cells → access nodes (deduplicated, demands summed, penalty = max priority),
  drives the solver.
- `app/infrastructure/networkx/graph.py` — `NetworkX` graph + cached
  `single_source_dijkstra` per source; depot-to-cell and pick-to-pick tables.
- `app/infrastructure/ortools/solver.py` — `ORToolSolver`: NxN distance matrix,
  Weight + Volume dimensions, one disjunction per pick node, `PATH_CHEAPEST_ARC` +
  guided local search.
- `app/entrypoints/` — FastAPI routers + Pydantic schemas + Jinja template
  (`GET /`).
- `app/infrastructure/database/db.py` — in-memory session store (single process,
  no TTL — demo only).

## Tests

```bash
uv run pytest -v
```

Layout mirrors the app: `tests/unit/...` for single-entity rules,
`tests/integration/...` for warehouse generation, graph mapping and solver
capacity checks. `pythonpath="."` is set in `pyproject.toml`; OR-Tools SWIG
`DeprecationWarning`s are filtered.

## Limits / next steps

- One cart, closed depot-to-depot tour; travel distance is minimized, handling time
  per tier/side is not modeled.
- No mid-route re-optimization endpoint yet (stateless recompute from picker
  position) and no naive-vs-optimized matplotlib comparison — both are natural
  follow-ups to the original spec.
