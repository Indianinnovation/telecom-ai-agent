import pandas as pd
import os

DATA_PATH = os.path.join(os.path.dirname(__file__), "../../data/kpi_data.csv")

def get_kpis(cell_id: str) -> dict:
    """Read KPI data for a given cell from CSV."""
    try:
        df = pd.read_csv(DATA_PATH)
        cell_df = df[df["cell_id"] == cell_id].tail(5)
        if cell_df.empty:
            return {"error": f"No KPI data found for {cell_id}"}
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
        return {"error": str(e)}
