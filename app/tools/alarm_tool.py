"""
Alarm Tool — Reads telecom alarm data from JSON.

This tool reads the alarms.json file and returns active alarms
for a given network element (ne_id).

Alarm severities: CRITICAL, MAJOR, MINOR
Alarm types: HIGH_PRB_UTILIZATION, THROUGHPUT_DROP, HIGH_BLER,
             HIGH_RETRANSMISSION, CELL_CONGESTION, LOW_SINR,
             LINK_FAILURE, POWER_DEGRADATION

Usage:
    from app.tools.alarm_tool import get_alarms
    result = get_alarms("CELL_001")

Debug:
    - If "error" key in result → check DATA_PATH and JSON file exists
    - If count=0 → no alarms for this cell (cell is healthy)
"""

import json
import os

# Path to the alarms JSON file (relative to this file's location)
DATA_PATH = os.path.join(os.path.dirname(__file__), "../../data/alarms.json")


def get_alarms(ne_id: str) -> dict:
    """
    Read active alarms for a given network element.

    Args:
        ne_id: Network element identifier (e.g., "CELL_001")

    Returns:
        dict with:
            - ne_id: the queried network element
            - alarms: list of alarm dicts
            - count: total number of alarms
            - critical: count of CRITICAL severity alarms
            - major: count of MAJOR severity alarms
        Returns {"error": "message"} on file error.

    Example:
        >>> get_alarms("CELL_001")
        {
            "ne_id": "CELL_001",
            "alarms": [...],
            "count": 2,
            "critical": 1,
            "major": 1
        }
    """
    try:
        # Read all alarms from JSON file
        with open(DATA_PATH, "r") as f:
            alarms = json.load(f)

        # Filter alarms for the requested network element
        cell_alarms = [a for a in alarms if a["ne_id"] == ne_id]

        # Return empty result if no alarms (cell is healthy)
        if not cell_alarms:
            return {"ne_id": ne_id, "alarms": [], "count": 0}

        # Count alarms by severity and return
        return {
            "ne_id": ne_id,
            "alarms": cell_alarms,
            "count": len(cell_alarms),
            "critical": sum(1 for a in cell_alarms if a["severity"] == "CRITICAL"),
            "major":    sum(1 for a in cell_alarms if a["severity"] == "MAJOR"),
        }
    except Exception as e:
        return {"error": str(e)}
