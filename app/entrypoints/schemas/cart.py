from pydantic import BaseModel, Field


class CartConfig(BaseModel): 
    max_weight: int = Field(gt=0, description="Cart weight capacity in kg.", examples=[78])
    max_volume: int = Field(gt=0, description="Cart volume capacity in volume units.", examples=[189])
