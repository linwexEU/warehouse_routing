### Warehouse Order-Picking Route Optimizer

**The specific problem:** given a warehouse layout and a picking list, compute the shortest valid route to collect all items, respecting a cart weight limit, and support re-optimizing mid-route when an item is missing from its expected slot.

- **Synthetic warehouse**: define a JSON topology — e.g. 20 aisles × 3 sections × 3 shelf tiers, each cell with coordinates and a routing-graph node ID, edges between adjacent walkable nodes with distance weights. Build this once as a generator script so you can demo different warehouse sizes.
- **Graph layer**: load topology into NetworkX; precompute a distance matrix between all storage cells using Dijkstra.
- **The actual optimization**: this is a Capacitated Vehicle Routing Problem variant (single vehicle = the cart) — solve with Google OR-Tools' routing solver: visit all required pick-cells in near-optimal order, respect max cart weight/volume, and if the full list doesn't fit under the cap, decide which items to leave behind (frame this as a secondary knapsack-style tradeoff — maximize value picked per unit distance).
- **Re-optimization endpoint**: given current picker position + remaining unfulfilled list, recompute the route from scratch — service must be stateless (no session/DB dependency on prior calls), state is always passed in by the caller.
- **API**: `POST /optimize` → ordered stop list, total distance, items skipped with reasons. Full OpenAPI/Swagger docs.
- **Tests**: pytest.
- **The visual proof**: render the warehouse graph with matplotlib, draw the naive nearest-neighbor route in one color and the OR-Tools optimized route in another, and quote the % distance saved.