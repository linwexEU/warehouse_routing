from pydantic import BaseModel, Field


class SPick(BaseModel): 
    cell_id: str = Field(description="Storage cell ID, e.g. A18-S11-R-T3.", examples=["A18-S11-R-T3"])
    quantity: int = Field(ge=1, description="Units to pick. Must not exceed stock in the cell.", examples=[2])
    priority: int = Field(ge=1, le=3, description="Pick value 1 (low) to 3 (high). Maps to OR-Tools drop penalty.", examples=[3])
