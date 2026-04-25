# 📡 Telecom Network Intelligence — AI Agent Platform

## Complete Documentation & User Guide

---

## 📋 Table of Contents

1. [Overview](#1-overview)
2. [Architecture](#2-architecture)
3. [Features](#3-features)
4. [Installation & Setup](#4-installation--setup)
5. [How to Use](#5-how-to-use)
6. [API Reference](#6-api-reference)
7. [Data Model](#7-data-model)
8. [Classification Logic](#8-classification-logic)
9. [Anomaly Detection Logic](#9-anomaly-detection-logic)
10. [Configuration Audit Logic](#10-configuration-audit-logic)
11. [Troubleshooting](#11-troubleshooting)
12. [Project Structure](#12-project-structure)

---

## 1. Overview

### What is this tool?

The **Telecom Network Intelligence Platform** is an AI-powered Root Cause Analysis (RCA) system
for telecom networks. It uses a **LangGraph agent workflow** combined with **OpenAI GPT-4o-mini**
to analyze network issues, detect anomalies, and provide actionable recommendations.

### Who is it for?

- **RAN Engineers** — Diagnose cell-level issues
- **NOC Operators** — Quick root cause identification
- **Network Planners** — Capacity and spectrum optimization
- **Management** — Executive dashboards and health scores

### What problems does it solve?

| Problem | Solution |
|---|---|
| Manual RCA takes hours | AI generates RCA in seconds |
| Unknown issue classification | LLM classifies using KPI + alarms + logs |
| Missed anomalies | Z-score + threshold detection catches outliers |
| Configuration drift | Automated config audit against baselines |
| No single dashboard | Unified UI with KPI, anomaly, config views |

---

## 2. Architecture

### System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        USER LAYER                                │
│                                                                   │
│   Streamlit UI (ui.py)          curl / API clients               │
│   http://localhost:8502          http://localhost:8000/docs       │
└──────────────┬──────────────────────────┬────────────────────────┘
               │                          │
               ▼                          ▼
┌─────────────────────────────────────────────────────────────────┐
│                      API LAYER (FastAPI)                          │
│                                                                   │
│   POST /analyze      — LangGraph agent RCA                       │
│   GET  /anomaly/{id} — Anomaly detection                         │
│   GET  /config/{id}  — Configuration audit                       │
│   GET  /health       — Health check                              │
└──────────────┬──────────────────────────────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────────────────────────────┐
│                   AGENT LAYER (LangGraph)                         │
│                                                                   │
│   ┌──────────┐   ┌──────────┐   ┌──────────┐   ┌────────────┐  │
│   │ CLASSIFY │──▶│ RETRIEVE │──▶│ ANALYZE  │──▶│ RECOMMEND  │  │
│   │ (LLM)    │   │ (Tools)  │   │ (LLM)    │   │ (LLM)      │  │
│   └──────────┘   └──────────┘   └──────────┘   └─────┬──────┘  │
│                                                        │         │
│                                                        ▼         │
│                                                  ┌──────────┐   │
│                                                  │ VALIDATE │   │
│                                                  │ (retry)  │   │
│                                                  └──────────┘   │
└──────────────┬──────────────────────────────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────────────────────────────┐
│                      TOOL LAYER                                   │
│                                                                   │
│   kpi_tool.py     — Reads KPI data from CSV                      │
│   alarm_tool.py   — Reads alarms from JSON                       │
│   log_tool.py     — Reads logs from TXT                          │
│   anomaly_tool.py — Z-score + threshold anomaly detection        │
│   config_tool.py  — Configuration audit against baselines        │
└──────────────┬──────────────────────────────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────────────────────────────┐
│                      DATA LAYER                                   │
│                                                                   │
│   data/kpi_data.csv   — 480+ rows, 10 cells, 7 KPIs             │
│   data/alarms.json    — 8 alarms (CRITICAL/MAJOR/MINOR)         │
│   data/logs.txt       — System logs with ERROR/WARN/INFO         │
└─────────────────────────────────────────────────────────────────┘
```

### LangGraph Agent Workflow

```
START
  │
  ▼
┌──────────────────────────────────────────────────────────┐
│ Node 1: CLASSIFY ISSUE                                    │
│                                                            │
│ Input:  User query + KPI data + Alarms + Logs             │
│ Logic:  LLM analyzes telemetry and classifies into:       │
│         congestion | interference | bler_issue |           │
│         link_failure | hardware_fault | coverage_issue |   │
│         healthy                                            │
│ Output: issue_type (single word)                           │
└──────────────┬───────────────────────────────────────────┘
               │
               ▼
┌──────────────────────────────────────────────────────────┐
│ Node 2: RETRIEVE DATA                                     │
│                                                            │
│ Input:  cell_id, ne_id                                    │
│ Logic:  Calls 3 tools:                                    │
│         - get_kpis(cell_id)  → avg KPIs from CSV          │
│         - get_alarms(ne_id)  → active alarms from JSON    │
│         - get_logs(ne_id)    → recent logs from TXT       │
│ Output: kpi_data, alarm_data, log_data                    │
│ Note:   Data already fetched in classify, pass-through    │
└──────────────┬───────────────────────────────────────────┘
               │
               ▼
┌──────────────────────────────────────────────────────────┐
│ Node 3: ANALYZE ISSUE                                     │
│                                                            │
│ Input:  issue_type + query + KPI + alarms + logs          │
│ Logic:  LLM performs Root Cause Analysis using all data    │
│ Output: analysis (3-4 sentence RCA)                       │
└──────────────┬───────────────────────────────────────────┘
               │
               ▼
┌──────────────────────────────────────────────────────────┐
│ Node 4: RECOMMEND ACTION                                  │
│                                                            │
│ Input:  issue_type + analysis + KPI summary               │
│ Logic:  LLM generates 3 actionable recommendations        │
│ Output: recommendation (numbered list)                    │
│         confidence (0.60 - 0.99 based on data quality)    │
└──────────────┬───────────────────────────────────────────┘
               │
               ▼
┌──────────────────────────────────────────────────────────┐
│ Node 5: VALIDATE OUTPUT                                   │
│                                                            │
│ Input:  analysis text                                     │
│ Logic:  Check if analysis is valid (>20 chars)            │
│         If invalid → retry (max 2 attempts)               │
│ Output: Final validated result                            │
└──────────────┬───────────────────────────────────────────┘
               │
               ▼
              END → JSON Response
```

---

## 3. Features

### Feature 1: 🔍 AI-Powered RCA (Analyze Tab)

**What it does:**
Accepts a natural language query about a network issue and returns:
- Issue classification (congestion, interference, etc.)
- Root cause analysis (3-4 sentences)
- 3 actionable recommendations
- Confidence score (0-99%)

**How it works:**
1. User enters query (e.g., "Throughput dropped on CELL_001")
2. LangGraph agent runs 5-node workflow
3. LLM classifies issue using real KPI + alarm + log data
4. LLM generates RCA and recommendations
5. Results displayed in professional card layout

**Single Cell Analysis:**
- Select one cell → Click "Run Analysis"

**Multi-Cell Batch Analysis:**
- Select multiple cells or "All" → Click "Run All Selected"
- Shows summary table + detail cards for each cell

**Network-Wide Scan (Sidebar):**
- Choose scan type (Spectrum Audit, PRB Optimization, etc.)
- Select cells → Click "Run Network Scan"
- Executive summary with issue distribution

### Feature 2: 📊 KPI Monitor Tab

**What it does:**
Real-time KPI dashboard for any selected cell.

**KPIs Monitored:**

| KPI | Warning | Critical | Unit |
|---|---|---|---|
| PRB Utilization | > 70% | > 85% | % |
| DL Throughput | < 30 | < 15 | Mbps |
| BLER | > 5% | > 10% | % |
| SINR | < 5 | < 0 | dB |
| RRC Connected | > 150 | > 250 | users |
| Latency | > 40 | > 80 | ms |

**Components:**
- 6 KPI scorecards with status (Normal/Warning/Critical)
- Throughput & PRB trend chart
- BLER & Retransmission trend chart
- Active alarms panel
- Raw KPI data table

### Feature 3: ⚠️ Anomaly Detection Tab

**What it does:**
Detects KPI anomalies using statistical analysis.

**Detection Methods:**

1. **Z-Score Analysis** (Statistical)
   - Calculates mean and standard deviation for each KPI
   - Flags values where |z-score| > 2.0
   - Catches outliers that deviate significantly from normal

2. **Threshold Analysis** (Rule-Based)
   - Compares latest value against warning/critical thresholds
   - Uses telecom industry standard thresholds

3. **Trend Detection** (Slope Analysis)
   - Analyzes last 5 samples using linear regression
   - Classifies trend as: Degrading ↑ | Stable → | Improving ↓

**Health Score Calculation:**
```
health_score = 100 - (critical_count × 25) - (warning_count × 10)

Score >= 80 → HEALTHY
Score >= 50 → DEGRADED
Score <  50 → CRITICAL
```

**Output:**
- Cell health score (0-100)
- Per-KPI cards with severity, trend, z-score
- Anomaly detail cards

### Feature 4: ⚙️ Configuration Audit Tab

**What it does:**
Audits cell configuration against baselines and maps alarms to misconfigurations.

**Two Types of Checks:**

1. **KPI-Based Config Checks:**
   - Compares actual KPI values against expected baselines
   - 7 parameters checked (PRB, Throughput, BLER, SINR, Latency, Retx, RRC)

2. **Alarm-Based Config Issues:**
   - Maps active alarms to likely configuration problems
   - 8 alarm types mapped to specific parameters

**Alarm → Configuration Mapping:**

| Alarm | Parameter | Recommendation |
|---|---|---|
| HIGH_PRB_UTILIZATION | Scheduler PRB Allocation | Reduce max PRB per UE |
| HIGH_BLER | MCS / CQI Configuration | Tune CQI reporting, adaptive MCS |
| HIGH_RETRANSMISSION | HARQ Configuration | Increase HARQ max retransmissions |
| LOW_SINR | Antenna / Power Config | Review antenna tilt, TX power |
| CELL_CONGESTION | Admission Control | Tighten RRC admission control |
| LINK_FAILURE | Transport / Backhaul | Verify S1 interface config |
| POWER_DEGRADATION | TX Power Configuration | Check power amplifier health |
| THROUGHPUT_DROP | QoS / Bearer Config | Optimize QCI mapping |

**Config Score Calculation:**
```
config_score = 100 - (critical_kpi × 20) - (warning_kpi × 10) - (alarm_critical × 15)

Score >= 80 → OPTIMAL
Score >= 50 → NEEDS TUNING
Score <  50 → MISCONFIGURED
```

### Feature 5: 📜 History Tab

**What it does:**
Tracks all analyses performed in the session.

**Components:**
- Summary metrics (total, avg confidence, top issue, unique cells)
- Issue distribution chart
- All analyses table
- Expandable detail cards per analysis

---

## 4. Installation & Setup

### Prerequisites

- Python 3.9+
- pip
- OpenAI API key (or AWS Bedrock access)

### Step-by-Step Setup

```bash
# 1. Clone the repository
git clone https://github.com/Indianinnovation/telecom-ai-agent.git
cd telecom-ai-agent

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate        # Mac/Linux
# venv\Scripts\activate         # Windows

# 3. Install dependencies
pip install -r requirements.txt

# 4. Add your API key
echo "OPENAI_API_KEY=your_key_here" > .env

# 5. Start API server (Terminal 1)
uvicorn app.main:app --reload --port 8000

# 6. Start UI (Terminal 2)
streamlit run ui.py

# 7. Open browser
# http://localhost:8502
```

### Verify Installation

```bash
# Check API is running
curl http://localhost:8000/health
# Expected: {"status":"ok","service":"Telecom AI Agent"}

# Check anomaly detection
curl http://localhost:8000/anomaly/CELL_001
# Expected: JSON with health_score, anomalies, etc.

# Check config audit
curl http://localhost:8000/config/CELL_001
# Expected: JSON with config_score, issues, etc.
```

---

## 5. How to Use

### 5.1 Quick Start (30 seconds)

1. Open `http://localhost:8502`
2. In the sidebar, click **📉 Throughput Drop**
3. See the analysis results on the right panel

### 5.2 Single Cell Analysis

1. Go to **🔍 Analyze** tab
2. Type a query: `Throughput dropped after 5 minutes`
3. Select Cell ID: `CELL_001`
4. Click **🔍 Run Analysis**
5. View: Issue type → Confidence → RCA → Recommendations

### 5.3 Multi-Cell Batch Analysis

1. Go to **🔍 Analyze** tab
2. Type a query
3. In "Or select multiple cells" → pick cells or check **All**
4. Click **🚀 Run All Selected**
5. View: Summary table → Detail cards per cell

### 5.4 Network-Wide Scan

1. In the sidebar → **🚀 Network-Wide Scan** section
2. Select scan type (e.g., "Spectrum Efficiency Audit")
3. Select cells or check **✅ Select All 10 Cells**
4. Click **🚀 Run Network Scan**
5. View: Executive summary → Issue distribution → Cell-by-cell results

### 5.5 Anomaly Detection

1. Go to **⚠️ Anomaly Detection** tab
2. Select a cell (try `CELL_001` for congestion anomalies)
3. View: Health score → KPI cards with severity/trend → Anomaly list

### 5.6 Configuration Audit

1. Go to **⚙️ Config Audit** tab
2. Select a cell
3. View: Config score → KPI checks → Alarm-based issues → Recommendations

### 5.7 Test Scenarios

| Scenario | Cell | Expected Result |
|---|---|---|
| Congestion | CELL_001 | PRB 98%, 302 users, 4.3 Mbps throughput |
| Interference | CELL_002 | BLER 28.7%, SINR -3.1 dB, retx 24.8% |
| Cell Congestion | CELL_003 | PRB 96.8%, 290 users, 172ms latency |
| Severe Interference | CELL_005 | BLER 32.1%, SINR -4.2 dB |
| Link Failure | CELL_007 | All KPIs at 0, 999ms latency (cell down) |
| Healthy | CELL_009 | Health score 100, no anomalies |

---

## 6. API Reference

### POST /analyze

**Request:**
```json
{
    "query": "Throughput dropped after 5 minutes",
    "cell_id": "CELL_001",
    "ne_id": "CELL_001"
}
```

**Response:**
```json
{
    "issue_type": "congestion",
    "analysis": "The root cause is high PRB utilization...",
    "recommendation": "1. Load balancing...\n2. Capacity expansion...",
    "confidence": 0.99,
    "cell_id": "CELL_001"
}
```

### GET /anomaly/{cell_id}

**Response:**
```json
{
    "cell_id": "CELL_001",
    "health_score": 0,
    "health_status": "critical",
    "anomaly_count": 5,
    "critical_count": 4,
    "warning_count": 0,
    "anomalies": [...],
    "kpi_summary": {...}
}
```

### GET /config/{cell_id}

**Response:**
```json
{
    "cell_id": "CELL_001",
    "config_score": 85,
    "config_status": "optimal",
    "total_issues": 2,
    "kpi_config_checks": [...],
    "alarm_config_issues": [...],
    "top_recommendations": [...]
}
```

### GET /health

**Response:**
```json
{
    "status": "ok",
    "service": "Telecom AI Agent"
}
```

---

## 7. Data Model

### kpi_data.csv

| Column | Type | Description |
|---|---|---|
| timestamp | datetime | Measurement time (30-min intervals) |
| cell_id | string | Cell identifier (CELL_001 to CELL_010) |
| prb_utilization | float | Physical Resource Block usage (%) |
| throughput_mbps | float | Downlink throughput (Mbps) |
| bler_pct | float | Block Error Rate (%) |
| retx_rate_pct | float | Retransmission rate (%) |
| sinr_db | float | Signal-to-Interference-plus-Noise Ratio (dB) |
| rrc_connected | int | Number of RRC connected users |
| latency_ms | float | Round-trip latency (ms) |

### alarms.json

| Field | Type | Description |
|---|---|---|
| alarm_id | string | Unique alarm identifier |
| ne_id | string | Network element (cell) ID |
| alarm_type | string | Alarm category |
| severity | string | CRITICAL / MAJOR / MINOR |
| timestamp | datetime | When alarm was raised |
| description | string | Human-readable description |
| status | string | ACTIVE / CLEARED |

### logs.txt

Format: `TIMESTAMP LEVEL [CELL_ID] Message`

Levels: INFO, WARN, ERROR

---

## 8. Classification Logic

The LLM receives **real telemetry data** (KPIs + alarms + logs) and classifies using these rules:

| Category | Rule |
|---|---|
| **congestion** | PRB > 80% OR RRC > 250 OR congestion alarm |
| **interference** | SINR < 3 dB AND BLER > 10% OR interference alarm |
| **bler_issue** | BLER > 10% OR retransmission alarm (when not interference) |
| **link_failure** | S1/X2/backhaul alarm OR "link failure" in logs |
| **hardware_fault** | TX power/antenna/VSWR alarm |
| **coverage_issue** | Low throughput + low PRB + low SINR |
| **healthy** | All KPIs nominal + no active alarms |

**Priority order** (when multiple issues): link_failure > hardware_fault > interference > congestion > bler_issue > coverage_issue > healthy

**Never returns "unknown"** — always picks best match.

---

## 9. Anomaly Detection Logic

### Algorithm

For each of the 7 KPIs:

```
1. Calculate mean(μ) and std(σ) across all samples for the cell
2. Calculate z-score = (latest_value - μ) / σ
3. If |z-score| > 2.0 → Statistical anomaly
4. If value exceeds warn/crit threshold → Threshold anomaly
5. Fit linear regression on last 5 samples → Trend detection
```

### Thresholds

| KPI | Warning | Critical | Direction |
|---|---|---|---|
| PRB Utilization | > 70% | > 85% | Higher is bad |
| Throughput | < 30 Mbps | < 15 Mbps | Lower is bad |
| BLER | > 5% | > 10% | Higher is bad |
| Retx Rate | > 5% | > 10% | Higher is bad |
| SINR | < 5 dB | < 0 dB | Lower is bad |
| RRC Connected | > 150 | > 250 | Higher is bad |
| Latency | > 40 ms | > 80 ms | Higher is bad |

### Health Score

```
health_score = 100 - (critical_anomalies × 25) - (warning_anomalies × 10)
Minimum: 0, Maximum: 100
```

---

## 10. Configuration Audit Logic

### KPI-Based Checks

Compares actual average KPI values against expected baselines:

| Parameter | Expected | Tolerance |
|---|---|---|
| Max RRC Connections | 250 | ±10 |
| PRB Utilization Target | 70% | ±10% |
| BLER Target | 2% | ±1% |
| SINR Target | 15 dB | ±5 dB |
| Latency Target | 20 ms | ±10 ms |
| Retx Rate Target | 2% | ±1% |
| Throughput Target | 100 Mbps | ±30 Mbps |

### Alarm-to-Config Mapping

Maps 8 alarm types to specific configuration parameters with recommendations.

### Config Score

```
config_score = 100 - (critical_kpi_issues × 20) - (warning_kpi_issues × 10) - (alarm_critical × 15)
```

---

## 11. Troubleshooting

### Common Issues

| Problem | Cause | Fix |
|---|---|---|
| "API Offline" in UI | API server not running | Run `uvicorn app.main:app --reload --port 8000` |
| "Error: Connection refused" | Wrong port | Check API runs on port 8000 |
| "No data for CELL_XXX" | Cell ID not in CSV | Use CELL_001 to CELL_010 |
| "invalid load key" | Wrong file format | Use `joblib.load()` not `pickle.load()` |
| Sidebar not visible | CSS hiding it | Check `initial_sidebar_state="expanded"` |
| "unknown" issue type | Old agent code | Update agent.py with new classification prompt |
| No anomalies detected | Normal data at end of CSV | Inject anomaly data (see data section) |
| Slow response | LLM API latency | Normal — takes 5-10 seconds per cell |

### Debug Steps

1. **Check API health:**
   ```bash
   curl http://localhost:8000/health
   ```

2. **Check API logs:**
   Look at the terminal running uvicorn for error messages.

3. **Test tools directly:**
   ```python
   from app.tools.kpi_tool import get_kpis
   from app.tools.anomaly_tool import detect_anomalies
   from app.tools.config_tool import audit_configuration

   print(get_kpis("CELL_001"))
   print(detect_anomalies("CELL_001"))
   print(audit_configuration("CELL_001"))
   ```

4. **Check .env file:**
   ```bash
   cat .env
   # Should show: OPENAI_API_KEY=sk-...
   ```

5. **Check Python syntax:**
   ```python
   python -c "import ast; ast.parse(open('ui.py').read()); print('OK')"
   ```

---

## 12. Project Structure

```
telecom_agent/
│
├── app/                          # Backend application
│   ├── __init__.py
│   ├── main.py                   # FastAPI entry point
│   │
│   ├── api/
│   │   ├── __init__.py
│   │   └── routes.py             # API endpoints (/analyze, /anomaly, /config, /health)
│   │
│   ├── graph/
│   │   ├── __init__.py
│   │   └── agent.py              # LangGraph 5-node agent workflow
│   │
│   ├── tools/
│   │   ├── __init__.py
│   │   ├── kpi_tool.py           # KPI reader (CSV)
│   │   ├── alarm_tool.py         # Alarm reader (JSON)
│   │   ├── log_tool.py           # Log reader (TXT)
│   │   ├── anomaly_tool.py       # Z-score + threshold anomaly detection
│   │   └── config_tool.py        # Configuration audit against baselines
│   │
│   └── models/
│       ├── __init__.py
│       └── schemas.py            # Pydantic request/response models
│
├── data/                         # Sample telecom data
│   ├── kpi_data.csv              # 498 rows, 10 cells, 7 KPIs
│   ├── alarms.json               # 8 alarms
│   └── logs.txt                  # System logs
│
├── ui.py                         # Streamlit McKinsey-style UI
├── requirements.txt              # Python dependencies
├── .env                          # API keys (NOT in git)
├── .gitignore                    # Protects .env
├── README.md                     # Quick start guide
└── DOCUMENTATION.md              # This file — full documentation
```

---

## License

MIT License — Free to use, modify, and distribute.

---

*Built with LangGraph + OpenAI + FastAPI + Streamlit*
*© 2024 Telecom AI Platform*
