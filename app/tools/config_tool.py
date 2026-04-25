"""
Configuration Audit Tool — Audits cell configuration against baselines.

This tool performs two types of configuration checks:

1. KPI-Based Config Checks:
   - Compares actual average KPI values against expected baselines
   - 7 parameters checked: PRB, Throughput, BLER, SINR, Latency, Retx, RRC
   - Each check returns: ok / warning / critical

2. Alarm-Based Config Issues:
   - Maps active alarms to likely configuration problems
   - 8 alarm types mapped to specific parameters and recommendations
   - Example: HIGH_PRB_UTILIZATION → "Scheduler PRB Allocation" misconfigured

Config Score Calculation:
   config_score = 100 - (critical_kpi × 20) - (warning_kpi × 10) - (alarm_critical × 15)
   Score >= 80 → OPTIMAL
   Score >= 50 → NEEDS TUNING
   Score <  50 → MISCONFIGURED

Usage:
    from app.tools.config_tool import audit_configuration
    result = audit_configuration("CELL_001")
    print(result["config_score"])           # 0-100
    print(result["alarm_config_issues"])    # list of config issues from alarms

Debug:
    - If config_score=100 → no issues found (cell config is optimal)
    - Check alarm_config_issues for alarm-to-config mapping
    - Check kpi_config_checks for all 7 KPI checks (including "ok" ones)
    - Modify CONFIG_BASELINE dict to adjust expected values
    - Modify ALARM_CONFIG_MAP dict to add new alarm-to-config mappings
"""

import json
import os
import pandas as pd

# Path to the data directory
DATA_PATH = os.path.join(os.path.dirname(__file__), "../../data")

# ── Expected Configuration Baselines ────────────────────────────────────────
# These represent the "ideal" configuration values for a healthy cell.
# "expected": target value, "tolerance": acceptable deviation
CONFIG_BASELINE = {
    "max_rrc_connections":    {"expected": 250,  "tolerance": 10,  "unit": "users"},
    "prb_utilization_target": {"expected": 70,   "tolerance": 10,  "unit": "%"},
    "bler_target":            {"expected": 2,    "tolerance": 1,   "unit": "%"},
    "sinr_target":            {"expected": 15,   "tolerance": 5,   "unit": "dB"},
    "latency_target":         {"expected": 20,   "tolerance": 10,  "unit": "ms"},
    "retx_rate_target":       {"expected": 2,    "tolerance": 1,   "unit": "%"},
    "throughput_target":      {"expected": 100,  "tolerance": 30,  "unit": "Mbps"},
}

# ── Alarm-to-Configuration Mapping ──────────────────────────────────────────
# Maps each alarm type to the likely misconfigured parameter.
# This is based on telecom domain knowledge:
#   - Each alarm type indicates a specific subsystem issue
#   - The "parameter" field tells which config to check
#   - The "recommendation" field gives actionable fix steps
ALARM_CONFIG_MAP = {
    "HIGH_PRB_UTILIZATION": {
        "parameter": "Scheduler PRB Allocation",
        "issue": "PRB scheduler may be misconfigured — max PRB limit too high",
        "recommendation": "Review and reduce max PRB allocation per UE. Enable dynamic PRB scheduling.",
        "severity": "critical"
    },
    "HIGH_BLER": {
        "parameter": "MCS / CQI Configuration",
        "issue": "MCS selection algorithm may be too aggressive for current channel conditions",
        "recommendation": "Tune CQI reporting interval. Enable adaptive MCS with conservative fallback.",
        "severity": "major"
    },
    "HIGH_RETRANSMISSION": {
        "parameter": "HARQ Configuration",
        "issue": "HARQ retransmission limit may be too low or HARQ process count insufficient",
        "recommendation": "Increase HARQ max retransmissions to 4. Review HARQ process configuration.",
        "severity": "major"
    },
    "LOW_SINR": {
        "parameter": "Antenna / Power Configuration",
        "issue": "TX power or antenna tilt may be misconfigured causing poor SINR",
        "recommendation": "Review antenna tilt (recommend 3-6 degrees). Check TX power settings.",
        "severity": "major"
    },
    "CELL_CONGESTION": {
        "parameter": "Admission Control",
        "issue": "Admission control thresholds may be too permissive",
        "recommendation": "Tighten RRC admission control. Enable load-based handover to neighboring cells.",
        "severity": "critical"
    },
    "LINK_FAILURE": {
        "parameter": "Transport / Backhaul Configuration",
        "issue": "S1/X2 interface configuration or backhaul link parameters may be incorrect",
        "recommendation": "Verify S1 interface IP/VLAN config. Check backhaul bandwidth and QoS settings.",
        "severity": "critical"
    },
    "POWER_DEGRADATION": {
        "parameter": "TX Power Configuration",
        "issue": "TX power configuration may be below optimal level",
        "recommendation": "Review reference signal power (RS Power). Check power amplifier health.",
        "severity": "major"
    },
    "THROUGHPUT_DROP": {
        "parameter": "QoS / Bearer Configuration",
        "issue": "QoS bearer configuration may not be optimized for current traffic mix",
        "recommendation": "Review GBR/non-GBR bearer split. Optimize QCI mapping for data services.",
        "severity": "major"
    },
}


def audit_configuration(cell_id: str) -> dict:
    """
    Audit cell configuration against baselines and alarm-based config issues.

    Args:
        cell_id: Cell identifier (e.g., "CELL_001")

    Returns:
        dict with:
            - cell_id: queried cell
            - config_score: 0-100 overall config health
            - config_status: "optimal" / "needs_tuning" / "misconfigured"
            - total_issues: total number of config issues found
            - critical_issues: number of critical issues
            - warning_issues: number of warning issues
            - kpi_config_checks: list of all 7 KPI checks (including "ok")
            - kpi_config_issues: list of KPI checks that are NOT "ok"
            - alarm_config_issues: list of alarm-to-config mappings
            - top_recommendations: top 3 prioritized recommendations
        Returns {"error": "message"} on error.

    Example:
        >>> audit_configuration("CELL_001")
        {
            "config_score": 85,
            "config_status": "optimal",
            "total_issues": 2,
            ...
        }
    """
    try:
        # ── Step 1: Load KPI data ───────────────────────────────────────────
        df = pd.read_csv(os.path.join(DATA_PATH, "kpi_data.csv"))
        cell_df = df[df["cell_id"] == cell_id].tail(10)  # Last 10 samples (~5 hours)

        # ── Step 2: Load alarms ─────────────────────────────────────────────
        with open(os.path.join(DATA_PATH, "alarms.json")) as f:
            all_alarms = json.load(f)
        cell_alarms = [a for a in all_alarms if a["ne_id"] == cell_id]

        config_issues = []  # KPI checks that failed
        config_checks = []  # All KPI checks (including passed)

        # ── Step 3: KPI-based configuration checks ──────────────────────────
        # Compare actual KPI averages against expected baselines
        if not cell_df.empty:
            # Calculate averages for all KPIs
            avg_prb  = cell_df["prb_utilization"].mean()
            avg_tput = cell_df["throughput_mbps"].mean()
            avg_bler = cell_df["bler_pct"].mean()
            avg_sinr = cell_df["sinr_db"].mean()
            avg_lat  = cell_df["latency_ms"].mean()
            avg_retx = cell_df["retx_rate_pct"].mean()
            avg_rrc  = cell_df["rrc_connected"].mean()

            # Define checks: (name, value, warn_threshold, crit_threshold,
            #                  higher_is_bad, parameter_name, recommendation)
            kpi_checks = [
                ("PRB Utilization",     avg_prb,  70,  85,  True,
                 "Scheduler PRB Allocation",
                 "PRB utilization exceeds target. Review scheduler configuration."),

                ("DL Throughput",       avg_tput, 70,  30,  False,
                 "Bearer / QoS Configuration",
                 "Throughput below target. Review QoS bearer and scheduling priority."),

                ("BLER",                avg_bler, 5,   10,  True,
                 "MCS / Link Adaptation",
                 "BLER above target. Tune link adaptation and CQI reporting."),

                ("SINR",                avg_sinr, 5,   0,   False,
                 "Antenna / Power Config",
                 "SINR below target. Review antenna tilt and TX power settings."),

                ("Latency",             avg_lat,  40,  80,  True,
                 "Transport / QoS Config",
                 "Latency above target. Review transport QoS and scheduling."),

                ("Retransmission Rate", avg_retx, 5,   10,  True,
                 "HARQ Configuration",
                 "Retransmission rate high. Review HARQ process configuration."),

                ("RRC Connections",     avg_rrc,  150, 250, True,
                 "Admission Control",
                 "RRC connections near capacity. Review admission control thresholds."),
            ]

            # Run each check
            for name, value, warn, crit, higher_is_bad, param, rec in kpi_checks:
                # Determine status based on direction
                if higher_is_bad:
                    status = "critical" if value >= crit else (
                        "warning" if value >= warn else "ok")
                else:
                    status = "critical" if value <= crit else (
                        "warning" if value <= warn else "ok")

                check = {
                    "check": name,
                    "parameter": param,
                    "measured_value": round(value, 2),
                    "warn_threshold": warn,
                    "crit_threshold": crit,
                    "status": status,
                    "recommendation": rec if status != "ok" else "Within nominal range",
                }
                config_checks.append(check)

                # Track failed checks separately
                if status != "ok":
                    config_issues.append(check)

        # ── Step 4: Alarm-based configuration issues ────────────────────────
        # Map each active alarm to a likely configuration problem
        alarm_config_issues = []
        for alarm in cell_alarms:
            alarm_type = alarm.get("alarm_type", "")
            if alarm_type in ALARM_CONFIG_MAP:
                cfg = ALARM_CONFIG_MAP[alarm_type]
                alarm_config_issues.append({
                    "alarm_type": alarm_type,
                    "severity": cfg["severity"],
                    "parameter": cfg["parameter"],
                    "issue": cfg["issue"],
                    "recommendation": cfg["recommendation"],
                    "alarm_timestamp": alarm.get("timestamp", ""),
                })

        # ── Step 5: Calculate config score ──────────────────────────────────
        # Deduct points for each issue found
        critical_issues = sum(1 for c in config_issues if c["status"] == "critical")
        warning_issues  = sum(1 for c in config_issues if c["status"] == "warning")
        alarm_critical  = sum(1 for a in alarm_config_issues if a["severity"] == "critical")

        config_score = max(0,
            100
            - (critical_issues * 20)   # -20 per critical KPI issue
            - (warning_issues * 10)    # -10 per warning KPI issue
            - (alarm_critical * 15)    # -15 per critical alarm-based issue
        )

        # Determine overall status
        config_status = (
            "optimal" if config_score >= 80 else
            ("needs_tuning" if config_score >= 50 else "misconfigured")
        )

        # ── Step 6: Return results ──────────────────────────────────────────
        return {
            "cell_id": cell_id,
            "config_score": config_score,
            "config_status": config_status,
            "total_issues": len(config_issues) + len(alarm_config_issues),
            "critical_issues": critical_issues + alarm_critical,
            "warning_issues": warning_issues,
            "kpi_config_checks": config_checks,       # All 7 checks
            "kpi_config_issues": config_issues,        # Only failed checks
            "alarm_config_issues": alarm_config_issues, # Alarm-to-config mappings
            "top_recommendations": [                    # Top 3 prioritized fixes
                c["recommendation"]
                for c in (config_issues + alarm_config_issues)[:3]
            ],
        }
    except Exception as e:
        return {"error": str(e)}
