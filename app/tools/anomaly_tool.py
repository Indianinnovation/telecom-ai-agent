"""
Anomaly Detection Tool — Detects KPI anomalies using statistical analysis.

This tool uses two methods to detect anomalies:

1. Z-Score Analysis (Statistical):
   - Calculates mean(μ) and standard deviation(σ) for each KPI
   - Flags values where |z-score| > 2.0 (configurable)
   - Catches outliers that deviate significantly from the cell's normal behavior

2. Threshold Analysis (Rule-Based):
   - Compares the latest KPI value against warning/critical thresholds
   - Uses telecom industry standard thresholds

3. Trend Detection (Slope Analysis):
   - Fits linear regression on the last 5 samples
   - Classifies trend as: degrading / stable / improving
   - Positive slope for "higher_is_bad" KPIs = degrading

Health Score Calculation:
   health_score = 100 - (critical_count × 25) - (warning_count × 10)
   Score >= 80 → HEALTHY
   Score >= 50 → DEGRADED
   Score <  50 → CRITICAL

Usage:
    from app.tools.anomaly_tool import detect_anomalies
    result = detect_anomalies("CELL_001")
    print(result["health_score"])      # 0-100
    print(result["anomalies"])         # list of anomaly dicts

Debug:
    - If health_score=100 and no anomalies → data at end of CSV is normal
    - Inject anomaly data at end of CSV to test (see DOCUMENTATION.md)
    - Adjust z_threshold parameter (default 2.0) for sensitivity
    - Check KPI_THRESHOLDS dict for threshold values
"""

import pandas as pd
import numpy as np
import os

# Path to the KPI data CSV file
DATA_PATH = os.path.join(os.path.dirname(__file__), "../../data/kpi_data.csv")

# ── KPI Thresholds ──────────────────────────────────────────────────────────
# These are telecom industry standard thresholds.
# "higher_is_bad": True  → value ABOVE threshold is bad (e.g., PRB, BLER)
# "higher_is_bad": False → value BELOW threshold is bad (e.g., throughput, SINR)
KPI_THRESHOLDS = {
    "prb_utilization":  {"warn": 70, "crit": 85, "unit": "%",    "higher_is_bad": True},
    "throughput_mbps":  {"warn": 30, "crit": 15, "unit": "Mbps", "higher_is_bad": False},
    "bler_pct":         {"warn": 5,  "crit": 10, "unit": "%",    "higher_is_bad": True},
    "retx_rate_pct":    {"warn": 5,  "crit": 10, "unit": "%",    "higher_is_bad": True},
    "sinr_db":          {"warn": 5,  "crit": 0,  "unit": "dB",   "higher_is_bad": False},
    "rrc_connected":    {"warn": 150,"crit": 250,"unit": "",     "higher_is_bad": True},
    "latency_ms":       {"warn": 40, "crit": 80, "unit": "ms",   "higher_is_bad": True},
}


def detect_anomalies(cell_id: str, z_threshold: float = 2.0) -> dict:
    """
    Detect KPI anomalies using Z-score + threshold analysis.

    Args:
        cell_id:     Cell identifier (e.g., "CELL_001")
        z_threshold: Z-score threshold for anomaly detection (default: 2.0)
                     Lower = more sensitive, Higher = fewer false positives

    Returns:
        dict with:
            - cell_id: queried cell
            - health_score: 0-100 overall health
            - health_status: "healthy" / "degraded" / "critical"
            - anomaly_count: total anomalies found
            - critical_count: number of critical anomalies
            - warning_count: number of warning anomalies
            - anomalies: list of anomaly detail dicts
            - kpi_summary: dict of all KPI analysis results
            - samples_analyzed: number of data points used
        Returns {"error": "message"} on error.
    """
    try:
        # ── Step 1: Load and filter data ────────────────────────────────────
        df = pd.read_csv(DATA_PATH)
        cell_df = df[df["cell_id"] == cell_id].copy()

        if cell_df.empty:
            return {"error": f"No data for {cell_id}"}

        anomalies = []    # List of detected anomalies
        kpi_summary = {}  # Summary of all KPI analysis

        # ── Step 2: Analyze each KPI ────────────────────────────────────────
        for kpi, thresholds in KPI_THRESHOLDS.items():
            if kpi not in cell_df.columns:
                continue  # Skip if KPI column doesn't exist

            values = cell_df[kpi].values  # All values for this KPI
            mean = np.mean(values)         # Historical mean
            std = np.std(values)           # Historical standard deviation
            latest = values[-1]            # Most recent value

            # ── Z-Score Calculation ─────────────────────────────────────────
            # z = (x - μ) / σ
            # |z| > 2.0 means the value is >2 standard deviations from mean
            z_score = (latest - mean) / std if std > 0 else 0
            is_z_anomaly = abs(z_score) > z_threshold

            # ── Threshold Check ─────────────────────────────────────────────
            # Compare latest value against warning and critical thresholds
            if thresholds["higher_is_bad"]:
                # For KPIs where higher = worse (PRB, BLER, latency, etc.)
                is_crit = latest >= thresholds["crit"]
                is_warn = latest >= thresholds["warn"]
            else:
                # For KPIs where lower = worse (throughput, SINR)
                is_crit = latest <= thresholds["crit"]
                is_warn = latest <= thresholds["warn"]

            # ── Trend Detection ─────────────────────────────────────────────
            # Use last 5 samples and fit a linear regression
            # Positive slope = increasing, Negative slope = decreasing
            recent = values[-5:] if len(values) >= 5 else values
            if len(recent) >= 3:
                # np.polyfit returns [slope, intercept]
                trend_slope = np.polyfit(range(len(recent)), recent, 1)[0]
                if thresholds["higher_is_bad"]:
                    # For "higher is bad" KPIs: positive slope = degrading
                    trend = "degrading" if trend_slope > 0.5 else (
                        "improving" if trend_slope < -0.5 else "stable")
                else:
                    # For "lower is bad" KPIs: negative slope = degrading
                    trend = "degrading" if trend_slope < -0.5 else (
                        "improving" if trend_slope > 0.5 else "stable")
            else:
                trend = "insufficient_data"
                trend_slope = 0

            # ── Determine Severity ──────────────────────────────────────────
            severity = "critical" if is_crit else (
                "warning" if is_warn else "normal")

            # ── Build KPI Entry ─────────────────────────────────────────────
            kpi_entry = {
                "kpi": kpi,
                "latest_value": round(float(latest), 2),
                "mean": round(float(mean), 2),
                "std": round(float(std), 2),
                "z_score": round(float(z_score), 2),
                "severity": severity,
                "trend": trend,
                "trend_slope": round(float(trend_slope), 3),
                "unit": thresholds["unit"],
                "threshold_warn": thresholds["warn"],
                "threshold_crit": thresholds["crit"],
            }

            # Store in summary (all KPIs, including normal ones)
            kpi_summary[kpi] = kpi_entry

            # ── Add to Anomalies if Flagged ─────────────────────────────────
            if is_z_anomaly or is_crit or is_warn:
                anomalies.append({
                    **kpi_entry,
                    "anomaly_type": "z_score" if is_z_anomaly else "threshold",
                    "description": (
                        f"{kpi}: {latest:.1f}{thresholds['unit']} "
                        f"(z={z_score:.1f}, mean={mean:.1f}, "
                        f"{'>' if thresholds['higher_is_bad'] else '<'} "
                        f"{'crit' if is_crit else 'warn'} threshold)"
                    )
                })

        # ── Step 3: Calculate Health Score ──────────────────────────────────
        # Each critical anomaly costs 25 points, each warning costs 10
        critical_count = sum(1 for a in anomalies if a["severity"] == "critical")
        warning_count = sum(1 for a in anomalies if a["severity"] == "warning")
        health_score = max(0, 100 - (critical_count * 25) - (warning_count * 10))

        # ── Step 4: Return Results ──────────────────────────────────────────
        return {
            "cell_id": cell_id,
            "anomaly_count": len(anomalies),
            "critical_count": critical_count,
            "warning_count": warning_count,
            "health_score": health_score,
            "health_status": (
                "healthy" if health_score >= 80 else
                ("degraded" if health_score >= 50 else "critical")
            ),
            "anomalies": anomalies,
            "kpi_summary": kpi_summary,
            "samples_analyzed": len(cell_df),
        }
    except Exception as e:
        return {"error": str(e)}
