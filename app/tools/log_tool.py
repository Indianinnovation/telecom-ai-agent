"""
Log Tool — Reads telecom system logs from TXT file.

This tool reads the logs.txt file and returns log entries
for a given network element (ne_id).

Log format: TIMESTAMP LEVEL [CELL_ID] Message
Levels: INFO, WARN, ERROR

Usage:
    from app.tools.log_tool import get_logs
    result = get_logs("CELL_001")

Debug:
    - If "error" key in result → check DATA_PATH and TXT file exists
    - If count=0 → no logs for this cell
    - recent_errors shows last 3 ERROR-level logs
"""

import os

# Path to the logs TXT file (relative to this file's location)
DATA_PATH = os.path.join(os.path.dirname(__file__), "../../data/logs.txt")


def get_logs(ne_id: str) -> dict:
    """
    Read logs for a given network element.

    Args:
        ne_id: Network element identifier (e.g., "CELL_001")

    Returns:
        dict with:
            - ne_id: the queried network element
            - logs: last 10 log lines for this cell
            - count: total log lines found
            - error_count: number of ERROR-level logs
            - warn_count: number of WARN-level logs
            - recent_errors: last 3 ERROR-level logs
        Returns {"error": "message"} on file error.

    Example:
        >>> get_logs("CELL_001")
        {
            "ne_id": "CELL_001",
            "logs": ["2024-01-01 10:00:00 ERROR [CELL_001] Congestion detected..."],
            "count": 8,
            "error_count": 4,
            "warn_count": 3,
            "recent_errors": [...]
        }
    """
    try:
        # Read all lines from the log file
        with open(DATA_PATH, "r") as f:
            lines = f.readlines()

        # Filter lines that contain the network element ID
        # Each log line has format: TIMESTAMP LEVEL [CELL_ID] Message
        cell_logs = [l.strip() for l in lines if ne_id in l]

        # Return empty result if no logs found
        if not cell_logs:
            return {"ne_id": ne_id, "logs": [], "count": 0}

        # Separate ERROR and WARN level logs for quick access
        errors = [l for l in cell_logs if "ERROR" in l]
        warns  = [l for l in cell_logs if "WARN"  in l]

        return {
            "ne_id":        ne_id,
            "logs":         cell_logs[-10:],   # Last 10 logs (most recent)
            "count":        len(cell_logs),     # Total log count
            "error_count":  len(errors),        # Number of ERROR logs
            "warn_count":   len(warns),         # Number of WARN logs
            "recent_errors": errors[-3:],       # Last 3 errors (for quick RCA)
        }
    except Exception as e:
        return {"error": str(e)}
