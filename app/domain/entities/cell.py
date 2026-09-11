from dataclasses import dataclass
from typing import Literal


@dataclass(frozen=True)
class Cell: 
    cell_id: str
    zone: Literal["A", "B", "C"]  # A - ambient, B - chilled, C - heavy
    aisle: int
    side: Literal["L", "R"]  # L - left, R - right
    section: int
    tier: int
    node_id: str
