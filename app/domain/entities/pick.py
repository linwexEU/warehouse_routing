from dataclasses import dataclass


@dataclass(frozen=True)
class Pick: 
    items: list[tuple[str, int, int]]  # [(cell_id, quantity, priority)]
