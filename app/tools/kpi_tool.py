"""
KPI Tool — Reads telecom KPI data from CSV.

This tool reads the kpi_data.csv file and returns average KPI values
for a given cell_id. It reads the last 5 samples to provide recent averages.

KPIs returned:
    - prb_utilization: Physical Resource Block usage (%)
    - throughput_mbps:  Downlink throughput (Mbps)
    - bler_pct:         Block Error Rate (%)
    - retx_rate_pct:    Retransmission rate (%)
    - sinr_db:          Signal-to-Interference-plus-Noise Ratio (dB)
    - rrc_connected:    Number of RRC connected users
    - latency_ms:       Round-trip latency (ms)

Usage:
    from app.tools.kpi_tool import get_kpis
    result = get_kpis("CELL_001")

Debug:
    - If "error" key in result → check DATA_PATH and CSV file exists
    - If empty result → cell_id not found in CSV (valid: CELL_001 to CELL_010)
"""

import pandas as pd
import os

# Path to the KPI data CSV file (relative to this file's location)
DATA_PATH = os.path.join(os.path.dirname(__file__), "../../data/kpi_data.csv")


def get_kpis(cell_id: str) -> dict:
    """
    Read KPI data for a given cell from CSV.

    Args:
        cell_id: Cell identifier (e.g., "CELL_001")

    Returns:
        dict with average KPI values for the last 5 samples.
        Returns {"error": "message"} if cell not found or file error.

    Example:
        >>> get_kpis("CELL_001")
        {
            "cell_id": "CELL_001",
            "avg_prb_utilization": 98.5,
            "avg_throughput_mbps": 4.3,
            ...
        }
    """
    try:
        # Read the full CSV file
        df = pd.read_csv(DATA_PATH)

        # Filter for the requested cell and take last 5 samples
        # Last 5 gives us the most recent ~2.5 hours of data (30-min intervals)
        cell_df = df[df["cell_id"] == cell_id].tail(5)

        # Return error if no data found for this cell
        if cell_df.empty:
            return {"error": f"No KPI data found for {cell_id}"}

        # Calculate averages for all KPIs and return
        return {
            "cell_id": cell_id,
            "avg_prb_utilization": round(cell_df["prb_utilization"].mean(), 2),
            "avg_throughput_mbps": round(cell_df["throughput_mbps"].mean(), 2),
            "avg_bler_pct":        round(cell_df["bler_pct"].mean(), 2),
            "avg_retx_rate_pct":   round(cell_df["retx_rate_pct"].mean(), 2),
            "avg_sinr_db":         round(cell_df["sinr_db"].mean(), 2),
            "avg_rrc_connected":   round(cell_df["rrc_connected"].mean(), 2),
            "avg_latency_ms":      round(cell_df["latency_ms"].mean(), 2),
            "latest_timestamp":    cell_df["timestamp"].iloc[-1],
        }
    except Exception as e:
        # Return error dict instead of raising — allows graceful handling upstream
        return {"error": str(e)}
