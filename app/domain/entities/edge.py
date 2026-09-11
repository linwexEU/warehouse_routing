from dataclasses import dataclass


@dataclass(frozen=True)
class Edge: 
    from_: str
    to_: str
    weight: float
    bidirectional: bool 
