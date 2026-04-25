# 📡 Real-Time Analytics & Self-Healing Engine — Technical Deep Dive

## Complete Logic Explanation

---

## 1. Overview — What Does This Engine Do?

The Real-Time Analytics Engine is the **brain** of the Telecom AI Agent.
It performs **5 layers of analysis** on every cell:

```
Layer 1: DATA INGESTION     → Read 16 KPIs from CSV (simulates real-time stream)
Layer 2: ANOMALY DETECTION  → Z-score + threshold + trend analysis per KPI
Layer 3: PATTERN DETECTION  → Detect multi-KPI degradation chains
Layer 4: HEALTH SCORING     → Calculate cell health (0-100) by category
Layer 5: SELF-HEALING       → Trigger automated corrective actions
```

### Why 5 Layers?

In real telecom networks, a single KPI anomaly (e.g., high BLER) is NOT enough
to diagnose the problem. You need to:
1. Detect the anomaly (Layer 2)
2. Understand the chain reaction (Layer 3) — BLER↑ because SINR↓ because interference
3. Know which subsystem is affected (Layer 4) — RF? Capacity? Mobility?
4. Take the right corrective action (Layer 5) — adjust power, not scheduler

---

## 2. Layer 1: Data Ingestion — 16 KPIs

### What KPIs are monitored?

```
┌─────────────────────────────────────────────────────────────────┐
│                    16 KPIs MONITORED                             │
├─────────────┬───────────────────────────────────────────────────┤
│ CATEGORY    │ KPIs                                              │
├─────────────┼───────────────────────────────────────────────────┤
│ Capacity    │ PRB Utilization (%), RRC Connected Users           │
│ Performance │ DL Throughput (Mbps), Latency (ms)                │
│ Quality     │ BLER (%), Retransmission Rate (%)                 │
│ RF          │ SINR (dB), RSRP (dBm), RSRQ (dB), CQI (0-15)   │
│ Mobility    │ HO Success Rate (%), HO Failures, RLF Count      │
│ Spectral    │ DL PRB Efficiency (bps/PRB)                      │
└─────────────┴───────────────────────────────────────────────────┘
```

### What does each KPI mean?

**Capacity KPIs:**
- `prb_utilization` — % of Physical Resource Blocks in use. Think of PRBs as
  "lanes on a highway". >85% = traffic jam.
- `rrc_connected` — Number of devices connected to the cell. >250 = overloaded.

**Performance KPIs:**
- `throughput_mbps` — How fast data is delivered. <15 Mbps = users complaining.
- `latency_ms` — Round-trip delay. >80ms = video calls buffering.

**Quality KPIs:**
- `bler_pct` — Block Error Rate. % of data blocks received with errors.
  >10% = interference or poor signal.
- `retx_rate_pct` — % of data that had to be re-sent. High retx = wasted resources.

**RF (Radio Frequency) KPIs:**
- `sinr_db` — Signal quality. <0 dB = interference is stronger than signal.
- `rsrp_dbm` — Signal strength. <-110 dBm = user is too far from tower.
- `rsrq_db` — Signal quality considering interference. <-15 dB = very poor.
- `cqi` — Channel Quality Indicator (0-15). <4 = can barely communicate.

**Mobility KPIs:**
- `ho_success_rate` — % of successful handovers between cells. <90% = dropped calls.
- `ho_failures` — Count of failed handovers. >20 = serious mobility issue.
- `rlf_count` — Radio Link Failures. >15 = users losing connection.

**Spectral Efficiency:**
- `dl_prb_efficiency` — Throughput per PRB. Low = wasting spectrum resources.

### How is data read?

```python
# File: app/tools/realtime_engine.py

# 1. Read the CSV file containing all cell KPI data
df = pd.read_csv(DATA_PATH)

# 2. Filter for the specific cell we're analyzing
cell_df = df[df["cell_id"] == cell_id].copy()

# 3. Each row = one 30-minute measurement interval
# 48 rows = 24 hours of data per cell
# The LAST row = most recent measurement (what we analyze)
```

**In production:** This would read from a real-time Kafka stream, OpenSearch,
or AWS Kinesis instead of CSV.

---

## 3. Layer 2: Anomaly Detection — 3 Methods

### Method 1: Z-Score Analysis (Statistical)

**What is Z-score?**
Z-score tells you "how many standard deviations away from normal is this value?"

```
Formula: z = (current_value - mean) / standard_deviation

Example for CELL_001 PRB Utilization:
  - Historical mean: 51.13%
  - Standard deviation: 25.45%
  - Current value: 98.5%

  z = (98.5 - 51.13) / 25.45 = 1.86

  |z| > 2.0 → ANOMALY (this is 1.86, close but not quite)
```

**Why Z-score?**
- It adapts to each cell's normal behavior
- CELL_001 normally runs at 50% PRB → 98% is abnormal
- CELL_010 normally runs at 80% PRB → 85% might be normal for it
- Z-score catches this difference automatically

**Code:**
```python
def _analyze_kpi(values, thresholds, z_threshold=2.0):
    # Step 1: Calculate statistics from ALL historical data
    mean = np.mean(values)      # Average value over time
    std = np.std(values)        # How much it normally varies
    latest = values[-1]         # Most recent measurement

    # Step 2: Calculate Z-score
    z_score = (latest - mean) / std if std > 0 else 0

    # Step 3: Flag if |z| exceeds threshold (default 2.0)
    # |z| > 2.0 means the value is in the top/bottom 2.3% of all values
    # This is statistically unusual
    is_z_anomaly = abs(z_score) > z_threshold
```

### Method 2: Threshold Analysis (Rule-Based)

**What are thresholds?**
Fixed limits based on telecom industry standards and 3GPP specifications.

```
┌──────────────────┬─────────┬──────────┬───────────────────┐
│ KPI              │ Warning │ Critical │ Direction         │
├──────────────────┼─────────┼──────────┼───────────────────┤
│ PRB Utilization  │ > 70%   │ > 85%    │ Higher = Bad      │
│ Throughput       │ < 30    │ < 15     │ Lower = Bad       │
│ BLER             │ > 5%    │ > 10%    │ Higher = Bad      │
│ SINR             │ < 5 dB  │ < 0 dB   │ Lower = Bad       │
│ RSRP             │ < -100  │ < -110   │ Lower = Bad       │
│ RSRQ             │ < -12   │ < -15    │ Lower = Bad       │
│ CQI              │ < 7     │ < 4      │ Lower = Bad       │
│ HO Success Rate  │ < 95%   │ < 90%    │ Lower = Bad       │
│ HO Failures      │ > 10    │ > 20     │ Higher = Bad      │
│ RLF Count        │ > 5     │ > 15     │ Higher = Bad      │
│ Latency          │ > 40 ms │ > 80 ms  │ Higher = Bad      │
│ RRC Connected    │ > 150   │ > 250    │ Higher = Bad      │
│ Retx Rate        │ > 5%    │ > 10%    │ Higher = Bad      │
│ PRB Efficiency   │ < 5     │ < 2      │ Lower = Bad       │
└──────────────────┴─────────┴──────────┴───────────────────┘
```

**Code:**
```python
    # "higher_is_bad" determines the comparison direction
    if thresholds["higher_is_bad"]:
        # For PRB, BLER, latency — higher values are worse
        is_crit = latest >= thresholds["crit"]   # e.g., PRB >= 85%
        is_warn = latest >= thresholds["warn"]   # e.g., PRB >= 70%
    else:
        # For throughput, SINR, RSRP — lower values are worse
        is_crit = latest <= thresholds["crit"]   # e.g., SINR <= 0 dB
        is_warn = latest <= thresholds["warn"]   # e.g., SINR <= 5 dB
```

### Method 3: Trend Analysis (Linear Regression)

**What is trend detection?**
Fits a straight line through the last 5 data points to see if the KPI
is getting better, worse, or staying the same.

```
Example: PRB Utilization last 5 samples
  Sample 1: 85%
  Sample 2: 90%
  Sample 3: 92%
  Sample 4: 95%
  Sample 5: 98%

  Linear regression slope = +3.3 (positive = increasing)
  Since PRB is "higher_is_bad" and slope > 0.5 → DEGRADING
```

**Code:**
```python
    # Take last 5 samples for trend analysis
    recent = values[-5:] if len(values) >= 5 else values

    if len(recent) >= 3:
        # np.polyfit fits a line: y = slope * x + intercept
        # We only care about the slope (first coefficient)
        trend_slope = np.polyfit(range(len(recent)), recent, 1)[0]

        if thresholds["higher_is_bad"]:
            # For "higher is bad" KPIs (PRB, BLER, latency):
            #   Positive slope = values going UP = DEGRADING
            #   Negative slope = values going DOWN = IMPROVING
            trend = "degrading" if trend_slope > 0.5 else (
                "improving" if trend_slope < -0.5 else "stable")
        else:
            # For "lower is bad" KPIs (throughput, SINR):
            #   Negative slope = values going DOWN = DEGRADING
            #   Positive slope = values going UP = IMPROVING
            trend = "degrading" if trend_slope < -0.5 else (
                "improving" if trend_slope > 0.5 else "stable")
```

### Combined Decision

A KPI is flagged as an anomaly if ANY of these is true:
```
is_anomaly = is_z_anomaly OR is_critical OR is_warning
```

---

## 4. Layer 3: Degradation Pattern Detection

### Why patterns matter

Single KPI anomalies don't tell the full story. In telecom, issues cascade:

```
CONGESTION CHAIN:
  Too many users (RRC↑)
    → PRB resources exhausted (PRB↑)
      → Throughput drops (Throughput↓)
        → Latency increases (Latency↑)
          → Handovers fail (HO failures↑)
            → Users drop calls

INTERFERENCE CHAIN:
  External interference or poor planning
    → SINR degrades (SINR↓)
      → Signal strength drops (RSRP↓)
        → Block errors increase (BLER↑)
          → Retransmissions increase (Retx↑)
            → Radio links fail (RLF↑)
              → Users lose connection
```

### 5 Patterns Detected

```
┌─────────────────────┬──────────────────────────────────────────────┬──────────┐
│ Pattern             │ Detection Rule                               │ Severity │
├─────────────────────┼──────────────────────────────────────────────┼──────────┤
│ Congestion Cascade  │ PRB > 80% AND Throughput < 20 Mbps          │ CRITICAL │
│ Interference Chain  │ SINR < 3 dB AND BLER > 10%                  │ CRITICAL │
│ Coverage Degradation│ RSRP < -110 dBm AND CQI < 7                │ MAJOR    │
│ Mobility Failure    │ HO Success < 90% AND RLF > 10              │ MAJOR    │
│ Capacity Exhaustion │ RRC > 200 AND PRB Efficiency < 5 bps/PRB   │ MAJOR    │
└─────────────────────┴──────────────────────────────────────────────┴──────────┘
```

**Code:**
```python
DEGRADATION_PATTERNS = {
    "congestion_chain": {
        # Lambda function checks if BOTH conditions are true simultaneously
        # This ensures we only flag congestion when BOTH PRB is high AND throughput is low
        # (High PRB alone might be normal during busy hour)
        "check": lambda d: d.get("prb_utilization", 0) > 80 and d.get("throughput_mbps", 999) < 20,
        ...
    },
}

# In run_realtime_analysis():
for pattern_id, pattern in DEGRADATION_PATTERNS.items():
    # Pass the latest KPI values to the pattern's check function
    if pattern["check"](latest_values):
        # Pattern is ACTIVE — this degradation chain is happening
        active_patterns.append(...)
```

---

## 5. Layer 4: Health Scoring

### Per-Category Health

KPIs are grouped into 6 categories. Each category gets its own health score:

```
Category Score = 100 - (critical_kpis × 30) - (warning_kpis × 15)
```

**Example for CELL_002:**
```
RF Category: SINR=critical, RSRP=critical, RSRQ=critical, CQI=critical
Score = 100 - (4 × 30) = 100 - 120 = 0 (CRITICAL)

Quality Category: BLER=critical, Retx=critical
Score = 100 - (2 × 30) = 100 - 60 = 40 (CRITICAL)

Capacity Category: PRB=normal, RRC=normal
Score = 100 - 0 = 100 (HEALTHY)
```

### Overall Health Score

```
health_score = 100
             - (critical_anomalies × 20)    # Each critical costs 20 points
             - (warning_anomalies × 8)       # Each warning costs 8 points
             - (active_patterns × 10)        # Each pattern costs 10 points

Minimum: 0, Maximum: 100

Score >= 80 → HEALTHY
Score >= 50 → DEGRADED
Score <  50 → CRITICAL
```

**Example for CELL_001:**
```
Critical anomalies: 4 (PRB, throughput, RRC, latency)
Warning anomalies: 2 (HO failures, RSRP)
Active patterns: 1 (Congestion Cascade)

health_score = 100 - (4×20) - (2×8) - (1×10)
             = 100 - 80 - 16 - 10
             = -6 → clamped to 0

Status: CRITICAL
```

---

## 6. Layer 5: Self-Healing Actions

### What is self-healing?

When a degradation pattern is detected, the engine recommends specific
corrective actions. Some can be executed automatically (AUTO), others
need human review (MANUAL).

### Action Types

```
┌─────────────────────┬──────────────────────────────────────────────┬──────┐
│ Action              │ What it does                                 │ Type │
├─────────────────────┼──────────────────────────────────────────────┼──────┤
│ LOAD_BALANCING      │ Move users to less busy neighbor cells       │ AUTO │
│ ADMISSION_CONTROL   │ Stop accepting new connections               │ AUTO │
│ QOS_REPRIORITIZE    │ Drop low-priority traffic first              │ AUTO │
│ POWER_ADJUSTMENT    │ Increase TX power to improve signal          │ AUTO │
│ TILT_OPTIMIZATION   │ Adjust antenna angle to reduce interference  │ AUTO │
│ MCS_FALLBACK        │ Use slower but more reliable modulation      │ AUTO │
│ POWER_BOOST         │ Increase power to extend coverage            │ AUTO │
│ TILT_REDUCTION      │ Reduce downtilt to cover more area           │ AUTO │
│ HO_PARAMETER_TUNE   │ Adjust handover trigger parameters           │ AUTO │
│ RSRP_THRESHOLD      │ Lower handover RSRP threshold                │ AUTO │
│ SCHEDULER_OPTIMIZE  │ Better PRB allocation algorithm              │ AUTO │
│ NEIGHBOR_ADD        │ Add missing neighbor cell relations           │ MANUAL│
│ NEIGHBOR_OPTIMIZE   │ Review neighbor cell list                     │ MANUAL│
│ CARRIER_AGGREGATION │ Enable multi-carrier for more capacity       │ MANUAL│
│ CELL_SPLIT          │ Deploy new small cell                         │ MANUAL│
└─────────────────────┴──────────────────────────────────────────────┴──────┘
```

### Why AUTO vs MANUAL?

- **AUTO** actions are safe, reversible, and well-understood.
  Example: Adjusting TX power by 2 dB is low-risk.

- **MANUAL** actions require planning, hardware changes, or coordination.
  Example: Deploying a new small cell requires site survey, permits, etc.

---

## 7. Complete Data Flow Example

### CELL_002 Analysis Walkthrough

```
INPUT: cell_id = "CELL_002"

STEP 1: Read 51 rows of KPI data for CELL_002

STEP 2: Analyze each KPI:
  ┌──────────────────┬─────────┬──────┬─────────┬──────────┬──────────┐
  │ KPI              │ Latest  │ Mean │ Z-Score │ Severity │ Trend    │
  ├──────────────────┼─────────┼──────┼─────────┼──────────┼──────────┤
  │ prb_utilization  │ 26.8%   │ 39.5 │ -1.05   │ normal   │ stable   │
  │ throughput_mbps  │ 55.1    │ 98.2 │ -1.24   │ normal   │ degrading│
  │ bler_pct         │ 28.7%   │ 6.0  │ +2.55   │ CRITICAL │ degrading│ ← ANOMALY
  │ retx_rate_pct    │ 24.8%   │ 4.5  │ +2.69   │ CRITICAL │ degrading│ ← ANOMALY
  │ sinr_db          │ -3.1 dB │ 14.8 │ -2.06   │ CRITICAL │ degrading│ ← ANOMALY
  │ rsrp_dbm         │ -113.1  │ -88  │ -2.1    │ CRITICAL │ degrading│ ← ANOMALY
  │ rsrq_db          │ -16.1   │ -11  │ -1.8    │ CRITICAL │ degrading│ ← ANOMALY
  │ cqi              │ 6.7     │ 11.2 │ -1.5    │ warning  │ degrading│ ← ANOMALY
  │ ho_success_rate  │ 86.6%   │ 96.5 │ -1.8    │ CRITICAL │ degrading│ ← ANOMALY
  │ ho_failures      │ 25      │ 5.2  │ +2.3    │ CRITICAL │ degrading│ ← ANOMALY
  │ rlf_count        │ 63      │ 8.5  │ +3.1    │ CRITICAL │ degrading│ ← ANOMALY
  └──────────────────┴─────────┴──────┴─────────┴──────────┴──────────┘

  Result: 9 anomalies (8 critical, 1 warning)

STEP 3: Check degradation patterns:
  ✅ Interference Chain: SINR(-3.1) < 3 AND BLER(28.7) > 10 → ACTIVE
  ✅ Coverage Chain:     RSRP(-113.1) < -110 AND CQI(6.7) < 7 → ACTIVE
  ✅ Mobility Chain:     HO_rate(86.6) < 90 AND RLF(63) > 10 → ACTIVE

  Result: 3 active patterns

STEP 4: Calculate health:
  Category health:
    capacity:    100 (healthy)
    performance: 100 (healthy)
    quality:     40  (critical)  — BLER + Retx both critical
    rf:          0   (critical)  — SINR + RSRP + RSRQ + CQI all bad
    mobility:    10  (critical)  — HO + RLF both critical
    spectral:    100 (healthy)

  Overall: 100 - (8×20) - (1×8) - (3×10) = 100 - 160 - 8 - 30 = 0

STEP 5: Trigger self-healing:
  From Interference Chain:
    🤖 AUTO → POWER_ADJUSTMENT: Increase TX power by 2-3 dB
    🤖 AUTO → TILT_OPTIMIZATION: Adjust antenna tilt
    🤖 AUTO → MCS_FALLBACK: Switch to conservative MCS

  From Coverage Chain:
    🤖 AUTO → POWER_BOOST: Increase cell TX power
    🤖 AUTO → TILT_REDUCTION: Reduce antenna downtilt
    👤 MANUAL → NEIGHBOR_ADD: Add missing neighbor relations

  From Mobility Chain:
    🤖 AUTO → HO_PARAMETER_TUNE: Adjust A3 offset and TTT
    👤 MANUAL → NEIGHBOR_OPTIMIZE: Review neighbor cell list
    🤖 AUTO → RSRP_THRESHOLD_ADJUST: Lower RSRP threshold

  Result: 7 auto-executable + 2 manual review

OUTPUT:
  {
    "cell_id": "CELL_002",
    "health_score": 0,
    "health_status": "critical",
    "anomaly_count": 9,
    "pattern_count": 3,
    "auto_executable_count": 7,
    "manual_review_count": 2
  }
```

---

## 8. How to Debug

### Check if data is loading correctly:
```python
from app.tools.realtime_engine import run_realtime_analysis
result = run_realtime_analysis("CELL_001")
print(result.get("error"))           # Should be None
print(result["samples_analyzed"])     # Should be ~51
print(result["kpis_monitored"])       # Should be 14
```

### Check specific KPI analysis:
```python
result = run_realtime_analysis("CELL_001")
prb = result["kpi_analysis"]["prb_utilization"]
print(f"Latest: {prb['latest_value']}")
print(f"Mean: {prb['mean']}")
print(f"Z-score: {prb['z_score']}")
print(f"Severity: {prb['severity']}")
print(f"Trend: {prb['trend']}")
```

### Check pattern detection:
```python
result = run_realtime_analysis("CELL_002")
for p in result["active_patterns"]:
    print(f"Pattern: {p['name']}")
    print(f"Severity: {p['severity']}")
    for a in p["self_healing_actions"]:
        print(f"  Action: {a['action']} (auto={a['auto_executable']})")
```

### Common issues:
- "No data for CELL_XXX" → Cell ID not in CSV (valid: CELL_001 to CELL_010)
- No anomalies detected → Last rows in CSV are normal. Inject anomaly data.
- JSON serialization error → numpy.bool not serializable. Use bool() wrapper.
- Pattern not triggering → Check lambda conditions in DEGRADATION_PATTERNS.

---

## 9. How to Extend

### Add a new KPI:
1. Add column to `kpi_data.csv`
2. Add threshold to `KPI_THRESHOLDS` dict in `realtime_engine.py`
3. The engine will automatically analyze it

### Add a new degradation pattern:
1. Add entry to `DEGRADATION_PATTERNS` dict
2. Define `check` lambda with conditions
3. Define `self_healing` actions
4. The engine will automatically detect it

### Add a new self-healing action:
1. Add to the relevant pattern's `self_healing` list
2. Set `auto_executable: True/False`
3. In production, connect to OSS/BSS API for actual execution

---

*Built with Python + NumPy + Pandas*
*Part of the Telecom Network Intelligence Platform*
