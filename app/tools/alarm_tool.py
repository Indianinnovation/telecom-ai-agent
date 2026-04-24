import json
import os

DATA_PATH = os.path.join(os.path.dirname(__file__), "../../data/alarms.json")

def get_alarms(ne_id: str) -> dict:
    """Read active alarms for a given network element."""
    try:
        with open(DATA_PATH, "r") as f:
            alarms = json.load(f)
        cell_alarms = [a for a in alarms if a["ne_id"] == ne_id]
        if not cell_alarms:
            return {"ne_id": ne_id, "alarms": [], "count": 0}
        return {
            "ne_id": ne_id,
            "alarms": cell_alarms,
            "count": len(cell_alarms),
            "critical": sum(1 for a in cell_alarms if a["severity"] == "CRITICAL"),
            "major":    sum(1 for a in cell_alarms if a["severity"] == "MAJOR"),
        }
    except Exception as e:
        return {"error": str(e)}
