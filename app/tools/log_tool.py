import os

DATA_PATH = os.path.join(os.path.dirname(__file__), "../../data/logs.txt")

def get_logs(ne_id: str) -> dict:
    """Read logs for a given network element."""
    try:
        with open(DATA_PATH, "r") as f:
            lines = f.readlines()
        cell_logs = [l.strip() for l in lines if ne_id in l]
        if not cell_logs:
            return {"ne_id": ne_id, "logs": [], "count": 0}
        errors = [l for l in cell_logs if "ERROR" in l]
        warns  = [l for l in cell_logs if "WARN"  in l]
        return {
            "ne_id":      ne_id,
            "logs":       cell_logs[-10:],  # last 10 logs
            "count":      len(cell_logs),
            "error_count": len(errors),
            "warn_count":  len(warns),
            "recent_errors": errors[-3:],
        }
    except Exception as e:
        return {"error": str(e)}
