from fastapi import APIRouter, HTTPException
from app.models.schemas import AnalyzeRequest, AnalyzeResponse
from app.graph.agent import agent
from app.tools.anomaly_tool import detect_anomalies
from app.tools.config_tool import audit_configuration
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

@router.get("/anomaly/{cell_id}")
async def anomaly_detection(cell_id: str):
    """Detect KPI anomalies using Z-score + threshold analysis."""
    try:
        logger.info(f"Anomaly detection for: {cell_id}")
        result = detect_anomalies(cell_id)
        if "error" in result:
            raise HTTPException(status_code=404, detail=result["error"])
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Anomaly error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/config/{cell_id}")
async def config_audit(cell_id: str):
    """Audit cell configuration against baselines."""
    try:
        logger.info(f"Config audit for: {cell_id}")
        result = audit_configuration(cell_id)
        if "error" in result:
            raise HTTPException(status_code=404, detail=result["error"])
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Config error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/health")
async def health():
    return {"status": "ok", "service": "Telecom AI Agent"}
