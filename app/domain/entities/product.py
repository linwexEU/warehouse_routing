from dataclasses import dataclass, field
import uuid


@dataclass
class Product: 
    product_id: str = field(default_factory=lambda: str(uuid.uuid4()).split("-")[-1], kw_only=True)
    weight_per_unit: int
    volume_per_unit: int
