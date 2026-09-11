from dataclasses import dataclass
from typing import Literal


@dataclass(frozen=True)
class Node: 
    node_id: str
    x: float
    y: float
    type_: Literal["cell_access", "junction", "depot"]
