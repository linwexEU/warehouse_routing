from pydantic import BaseModel, Field

from app.domain.entities.cell import Cell


class SCell(BaseModel): 
    cell_id: str = Field(description="Storage cell ID.", examples=["A1-S1-L-T1"])
    zone: str = Field(description="Warehouse zone: A (ambient), B (chilled), C (heavy).", examples=["A"])
    aisle: int = Field(description="1-based aisle number.", examples=[1])
    side: str = Field(description="Rack side: L or R.", examples=["L"])
    section: int = Field(description="Section number within the aisle.", examples=[1])
    tier: int = Field(description="Tier/level, 1-based.", examples=[1])
    node_id: str = Field(description="Routing access node this cell hangs off (18 cells share one).", examples=["N0-A0"])
    
    @staticmethod
    def from_entity(cell: Cell) -> "SCell": 
        return SCell(
            cell_id=cell.cell_id,
            zone=cell.zone, 
            aisle=cell.aisle,
            side=cell.side,
            section=cell.section,
            tier=cell.tier,
            node_id=cell.node_id
        )
    
    
class CellsInfo(BaseModel): 
    cells: list[SCell] = Field(description="Page of storage cells.")
    total: int = Field(description="Total cells in the generated warehouse.")
    limit: int = Field(description="Page size requested.")
    offset: int = Field(description="Offset requested.")
    
    @staticmethod
    def from_entity(cells: list[Cell], total: int, limit: int, offset: int) -> "CellsInfo": 
        return CellsInfo(
            cells=[SCell.from_entity(cell) for cell in cells],
            total=total,
            limit=limit,
            offset=offset,
        )
