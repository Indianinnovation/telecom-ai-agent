from fastapi import APIRouter, HTTPException
from app.models.schemas import AnalyzeRequest, AnalyzeResponse
from app.graph.agent import agent
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/analyze", response_model=AnalyzeResponse)
async def analyze(request: AnalyzeRequest):
    try:
        logger.info(f"Analyzing query: {request.query}")
        result = agent.invoke({
            "query":       request.query,
            "cell_id":     request.cell_id,
            "ne_id":       request.ne_id,
            "issue_type":  "",
            "kpi_data":    {},
            "alarm_data":  {},
            "log_data":    {},
            "analysis":    "",
            "recommendation": "",
            "confidence":  0.0,
            "retry_count": 0,
            "messages":    [],
        })
        return AnalyzeResponse(
            issue_type=     result["issue_type"],
            analysis=       result["analysis"],
            recommendation= result["recommendation"],
            confidence=     result["confidence"],
            cell_id=        result["cell_id"],
        )
    except Exception as e:
        logger.error(f"Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/health")
async def health():
    return {"status": "ok", "service": "Telecom AI Agent"}
