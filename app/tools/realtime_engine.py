"""
Real-Time Analytics & Anomaly Detection Engine

Monitors real-time network performance streams, detects degradation patterns,
and triggers automated corrective workflows.

KPIs Monitored (16 total):
    Core:     PRB Utilization, Throughput, BLER, Retx Rate, SINR, RRC, Latency
    RF:       RSRP (dBm), RSRQ (dB), CQI (0-15)
    Mobility: Handover Success Rate (%), Handover Failures, RLF Count
    Spectral: DL PRB Efficiency (bps/PRB)

Detection Methods:
    1. Z-Score Analysis — statistical outlier detection
    2. Threshold Breach — rule-based warning/critical
    3. Trend Analysis — linear regression on recent samples
    4. Degradation Pattern Detection — multi-KPI correlation chains
    5. Self-Healing Trigger — automated corrective action recommendations

Degradation Patterns Detected:
    - Congestion Chain:    PRB↑ → Throughput↓ → Latency↑ → HO failures↑
    - Interference Chain:  SINR↓ → RSRP↓ → BLER↑ → Retx↑ → RLF↑
    - Coverage Chain:      RSRP↓ → RSRQ↓ → CQI↓ → Throughput↓
    - Mobility Chain:      HO failures↑ → RLF↑ → Dropped calls
    - Capacity Chain:      RRC↑ → PRB↑ → Spectral efficiency↓

Self-Healing Actions:
    - Load balancing trigger
    - Power/tilt adjustment
    - Admission control tightening
    - HARQ/MCS reconfiguration
    - Neighbor cell offload

Usage:
    from app.tools.realtime_engine import run_realtime_analysis
    result = run_realtime_analysis("CELL_001")
"""

import pandas as pd
import numpy as np
import os
from datetime import datetime

DATA_PATH = os.path.join(os.path.dirname(__file__), "../../data/kpi_data.csv")

# ── Full KPI Thresholds (16 KPIs) ──────────────────────────────────────────
KPI_THRESHOLDS = {
    # Core KPIs
    "prb_utilization":   {"warn": 70,   "crit": 85,   "unit": "%",      "higher_is_bad": True,  "category": "capacity"},
    "throughput_mbps":   {"warn": 30,   "crit": 15,   "unit": "Mbps",   "higher_is_bad": False, "category": "performance"},
    "bler_pct":          {"warn": 5,    "crit": 10,   "unit": "%",      "higher_is_bad": True,  "category": "quality"},
    "retx_rate_pct":     {"warn": 5,    "crit": 10,   "unit": "%",      "higher_is_bad": True,  "category": "quality"},
    "sinr_db":           {"warn": 5,    "crit": 0,    "unit": "dB",     "higher_is_bad": False, "category": "rf"},
    "rrc_connected":     {"warn": 150,  "crit": 250,  "unit": "",       "higher_is_bad": True,  "category": "capacity"},
    "latency_ms":        {"warn": 40,   "crit": 80,   "unit": "ms",     "higher_is_bad": True,  "category": "performance"},
    # RF KPIs
    "rsrp_dbm":          {"warn": -100, "crit": -110, "unit": "dBm",    "higher_is_bad": False, "category": "rf"},
    "rsrq_db":           {"warn": -12,  "crit": -15,  "unit": "dB",     "higher_is_bad": False, "category": "rf"},
    "cqi":               {"warn": 7,    "crit": 4,    "unit": "",       "higher_is_bad": False, "category": "rf"},
    # Mobility KPIs
    "ho_success_rate":   {"warn": 95,   "crit": 90,   "unit": "%",      "higher_is_bad": False, "category": "mobility"},
    "ho_failures":       {"warn": 10,   "crit": 20,   "unit": "",       "higher_is_bad": True,  "category": "mobility"},
    "rlf_count":         {"warn": 5,    "crit": 15,   "unit": "",       "higher_is_bad": True,  "category": "mobility"},
    # Spectral Efficiency
    "dl_prb_efficiency": {"warn": 5,    "crit": 2,    "unit": "bps/PRB","higher_is_bad": False, "category": "spectral"},
}

# ── Degradation Pattern Definitions ─────────────────────────────────────────
# Each pattern defines a chain of correlated KPI degradations.
# "kpis": list of KPIs involved in the chain
# "conditions": lambda functions that check if the pattern is active
# "severity": how critical this pattern is
# "self_healing": automated corrective actions to trigger
DEGRADATION_PATTERNS = {
    "congestion_chain": {
        "name": "Congestion Cascade",
        "description": "High PRB utilization causing throughput drop, latency spike, and handover failures",
        "kpis": ["prb_utilization", "throughput_mbps", "latency_ms", "ho_failures", "rrc_connected"],
        "check": lambda d: d.get("prb_utilization", 0) > 80 and d.get("throughput_mbps", 999) < 20,
        "severity": "critical",
        "self_healing": [
            {"action": "LOAD_BALANCING", "description": "Trigger inter-cell load balancing to offload traffic to neighbor cells",
             "parameter": "MLB (Mobility Load Balancing)", "auto_executable": True},
            {"action": "ADMISSION_CONTROL", "description": "Tighten RRC admission control to prevent new connections",
             "parameter": "RRC Connection Limit", "auto_executable": True},
            {"action": "QOS_REPRIORITIZE", "description": "Reprioritize QoS bearers — drop non-GBR traffic first",
             "parameter": "QCI Priority Table", "auto_executable": True},
        ]
    },
    "interference_chain": {
        "name": "Interference Cascade",
        "description": "Low SINR causing RSRP/RSRQ degradation, high BLER, retransmissions, and radio link failures",
        "kpis": ["sinr_db", "rsrp_dbm", "bler_pct", "retx_rate_pct", "rlf_count"],
        "check": lambda d: d.get("sinr_db", 99) < 3 and d.get("bler_pct", 0) > 10,
        "severity": "critical",
        "self_healing": [
            {"action": "POWER_ADJUSTMENT", "description": "Increase TX power by 2-3 dB to improve SINR",
             "parameter": "RS Power / PA Power", "auto_executable": True},
            {"action": "TILT_OPTIMIZATION", "description": "Adjust antenna electrical tilt to reduce interference",
             "parameter": "Antenna E-Tilt", "auto_executable": True},
            {"action": "MCS_FALLBACK", "description": "Switch to conservative MCS to reduce BLER",
             "parameter": "Link Adaptation / MCS Table", "auto_executable": True},
        ]
    },
    "coverage_chain": {
        "name": "Coverage Degradation",
        "description": "Weak RSRP causing poor RSRQ, low CQI, and throughput degradation",
        "kpis": ["rsrp_dbm", "rsrq_db", "cqi", "throughput_mbps"],
        "check": lambda d: d.get("rsrp_dbm", 0) < -110 and d.get("cqi", 15) < 7,
        "severity": "major",
        "self_healing": [
            {"action": "POWER_BOOST", "description": "Increase cell TX power to extend coverage",
             "parameter": "Max TX Power", "auto_executable": True},
            {"action": "TILT_REDUCTION", "description": "Reduce antenna downtilt to extend coverage footprint",
             "parameter": "Antenna Mechanical/Electrical Tilt", "auto_executable": True},
            {"action": "NEIGHBOR_ADD", "description": "Add missing neighbor relations for better handover",
             "parameter": "ANR (Automatic Neighbor Relations)", "auto_executable": False},
        ]
    },
    "mobility_chain": {
        "name": "Mobility Failure Chain",
        "description": "High handover failures and radio link failures indicating mobility issues",
        "kpis": ["ho_success_rate", "ho_failures", "rlf_count"],
        "check": lambda d: d.get("ho_success_rate", 100) < 90 and d.get("rlf_count", 0) > 10,
        "severity": "major",
        "self_healing": [
            {"action": "HO_PARAMETER_TUNE", "description": "Adjust A3 offset and TTT for earlier handover trigger",
             "parameter": "A3 Offset / Time-to-Trigger", "auto_executable": True},
            {"action": "NEIGHBOR_OPTIMIZE", "description": "Review and optimize neighbor cell list",
             "parameter": "Neighbor Relations Table", "auto_executable": False},
            {"action": "RSRP_THRESHOLD_ADJUST", "description": "Lower RSRP threshold for handover trigger",
             "parameter": "A2/B2 RSRP Threshold", "auto_executable": True},
        ]
    },
    "capacity_chain": {
        "name": "Capacity Exhaustion",
        "description": "High RRC connections exhausting PRB resources and reducing spectral efficiency",
        "kpis": ["rrc_connected", "prb_utilization", "dl_prb_efficiency"],
        "check": lambda d: d.get("rrc_connected", 0) > 200 and d.get("dl_prb_efficiency", 99) < 5,
        "severity": "major",
        "self_healing": [
            {"action": "CARRIER_AGGREGATION", "description": "Enable carrier aggregation to increase capacity",
             "parameter": "CA Configuration", "auto_executable": False},
            {"action": "SCHEDULER_OPTIMIZE", "description": "Optimize PRB scheduler for better resource allocation",
             "parameter": "Proportional Fair Scheduler", "auto_executable": True},
            {"action": "CELL_SPLIT", "description": "Recommend cell split or small cell deployment",
             "parameter": "Network Planning", "auto_executable": False},
        ]
    },
}


def _analyze_kpi(values: np.ndarray, thresholds: dict, z_threshold: float = 2.0) -> dict:
    """Analyze a single KPI: z-score, threshold, trend."""
    mean = np.mean(values)
    std = np.std(values)
    latest = values[-1]

    # Z-score
    z_score = (latest - mean) / std if std > 0 else 0
    is_z_anomaly = abs(z_score) > z_threshold

    # Threshold
    if thresholds["higher_is_bad"]:
        is_crit = latest >= thresholds["crit"]
        is_warn = latest >= thresholds["warn"]
    else:
        is_crit = latest <= thresholds["crit"]
        is_warn = latest <= thresholds["warn"]

    # Trend (last 5 samples)
    recent = values[-5:] if len(values) >= 5 else values
    if len(recent) >= 3:
        trend_slope = np.polyfit(range(len(recent)), recent, 1)[0]
        if thresholds["higher_is_bad"]:
            trend = "degrading" if trend_slope > 0.5 else ("improving" if trend_slope < -0.5 else "stable")
        else:
            trend = "degrading" if trend_slope < -0.5 else ("improving" if trend_slope > 0.5 else "stable")
    else:
        trend = "insufficient_data"
        trend_slope = 0

    severity = "critical" if is_crit else ("warning" if is_warn else "normal")

    return {
        "latest_value": round(float(latest), 2),
        "mean": round(float(mean), 2),
        "std": round(float(std), 2),
        "z_score": round(float(z_score), 2),
        "is_z_anomaly": is_z_anomaly,
        "severity": severity,
        "trend": trend,
        "trend_slope": round(float(trend_slope), 3),
        "is_anomaly": is_z_anomaly or is_crit or is_warn,
    }


def run_realtime_analysis(cell_id: str) -> dict:
    """
    Run full real-time analytics: anomaly detection + degradation patterns + self-healing.

    Args:
        cell_id: Cell identifier (e.g., "CELL_001")

    Returns:
        dict with:
            - cell_id, timestamp
            - health_score (0-100), health_status
            - kpi_analysis: per-KPI analysis (16 KPIs)
            - anomalies: list of detected anomalies
            - degradation_patterns: active degradation chains
            - self_healing_actions: triggered corrective workflows
            - category_health: health by category (capacity, performance, rf, mobility, spectral)
    """
    try:
        df = pd.read_csv(DATA_PATH)
        cell_df = df[df["cell_id"] == cell_id].copy()
        if cell_df.empty:
            return {"error": f"No data for {cell_id}"}

        # ── Step 1: Analyze all 16 KPIs ─────────────────────────────────────
        kpi_analysis = {}
        anomalies = []
        latest_values = {}  # For pattern detection

        for kpi, thresholds in KPI_THRESHOLDS.items():
            if kpi not in cell_df.columns:
                continue

            values = cell_df[kpi].values
            result = _analyze_kpi(values, thresholds)
            result["kpi"] = kpi
            result["unit"] = thresholds["unit"]
            result["category"] = thresholds["category"]
            result["threshold_warn"] = thresholds["warn"]
            result["threshold_crit"] = thresholds["crit"]
            kpi_analysis[kpi] = result
            latest_values[kpi] = result["latest_value"]

            if result["is_anomaly"]:
                anomalies.append({
                    **result,
                    "description": (
                        f"{kpi}: {result['latest_value']}{thresholds['unit']} "
                        f"(z={result['z_score']}, severity={result['severity']}, trend={result['trend']})"
                    )
                })

        # ── Step 2: Detect Degradation Patterns ─────────────────────────────
        active_patterns = []
        all_healing_actions = []

        for pattern_id, pattern in DEGRADATION_PATTERNS.items():
            try:
                if pattern["check"](latest_values):
                    # Collect KPI details for this pattern
                    pattern_kpis = {}
                    for kpi_name in pattern["kpis"]:
                        if kpi_name in kpi_analysis:
                            pattern_kpis[kpi_name] = kpi_analysis[kpi_name]

                    active_patterns.append({
                        "pattern_id": pattern_id,
                        "name": pattern["name"],
                        "description": pattern["description"],
                        "severity": pattern["severity"],
                        "affected_kpis": pattern_kpis,
                        "self_healing_actions": pattern["self_healing"],
                    })

                    # Collect all healing actions
                    for action in pattern["self_healing"]:
                        all_healing_actions.append({
                            **action,
                            "triggered_by": pattern["name"],
                            "pattern_severity": pattern["severity"],
                            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        })
            except Exception:
                continue  # Skip pattern if check fails

        # ── Step 3: Category Health ─────────────────────────────────────────
        categories = {}
        for kpi_name, kpi_data in kpi_analysis.items():
            cat = kpi_data["category"]
            if cat not in categories:
                categories[cat] = {"total": 0, "critical": 0, "warning": 0, "normal": 0}
            categories[cat]["total"] += 1
            categories[cat][kpi_data["severity"]] += 1

        category_health = {}
        for cat, counts in categories.items():
            score = max(0, 100 - (counts["critical"] * 30) - (counts["warning"] * 15))
            category_health[cat] = {
                "score": score,
                "status": "healthy" if score >= 80 else ("degraded" if score >= 50 else "critical"),
                **counts
            }

        # ── Step 4: Overall Health Score ────────────────────────────────────
        critical_count = sum(1 for a in anomalies if a["severity"] == "critical")
        warning_count = sum(1 for a in anomalies if a["severity"] == "warning")
        pattern_penalty = len(active_patterns) * 10
        health_score = max(0, 100 - (critical_count * 20) - (warning_count * 8) - pattern_penalty)

        return {
            "cell_id": cell_id,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "samples_analyzed": len(cell_df),
            "kpis_monitored": len(kpi_analysis),
            # Health
            "health_score": health_score,
            "health_status": "healthy" if health_score >= 80 else ("degraded" if health_score >= 50 else "critical"),
            # Anomalies
            "anomaly_count": len(anomalies),
            "critical_count": critical_count,
            "warning_count": warning_count,
            "anomalies": anomalies,
            # KPI Analysis
            "kpi_analysis": kpi_analysis,
            "category_health": category_health,
            # Degradation Patterns
            "active_patterns": active_patterns,
            "pattern_count": len(active_patterns),
            # Self-Healing
            "self_healing_actions": all_healing_actions,
            "auto_executable_count": sum(1 for a in all_healing_actions if a.get("auto_executable")),
            "manual_review_count": sum(1 for a in all_healing_actions if not a.get("auto_executable")),
        }
    except Exception as e:
        return {"error": str(e)}
