from pydantic import BaseModel
from typing import Optional

class AnalyzeRequest(BaseModel):
    query: str
    cell_id: Optional[str] = "CELL_001"
    ne_id: Optional[str] = "CELL_001"

class AnalyzeResponse(BaseModel):
    issue_type: str
    analysis: str
    recommendation: str
    confidence: float
    cell_id: str
