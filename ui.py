import streamlit as st
import requests
import json
import pandas as pd
import time
from datetime import datetime

# ── Page Config ─────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Telecom AI Agent | RCA Platform",
    page_icon="📡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── McKinsey Design System ───────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

/* ── Reset & Base ── */
* { font-family: 'Inter', sans-serif !important; box-sizing: border-box; }
.stApp { background-color: #f7f8fa; }
#MainMenu, footer { visibility: hidden; }

/* ── Force sidebar always visible ── */
[data-testid="stSidebar"] { display: flex !important; }
[data-testid="collapsedControl"] { display: none !important; }
section[data-testid="stSidebar"] { min-width: 280px !important; max-width: 280px !important; transform: none !important; }

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background: #0d2b4e !important;
    border-right: none;
    padding-top: 0;
}
[data-testid="stSidebar"] * { color: #e8edf2 !important; }
[data-testid="stSidebar"] .stSelectbox label { color: #94a3b8 !important; font-size: 11px !important; text-transform: uppercase; letter-spacing: 1px; }
[data-testid="stSidebar"] .stSelectbox > div > div {
    background: #1a3a5c !important;
    border: 1px solid #2d5a8e !important;
    color: #e8edf2 !important;
    border-radius: 6px;
}
[data-testid="stSidebar"] hr { border-color: #1e3d5c !important; }

/* ── Sidebar Buttons ── */
[data-testid="stSidebar"] .stButton > button {
    background: transparent !important;
    border: 1px solid #2d5a8e !important;
    color: #94b8d4 !important;
    border-radius: 6px !important;
    font-size: 12px !important;
    font-weight: 500 !important;
    padding: 8px 12px !important;
    width: 100% !important;
    text-align: left !important;
    transition: all 0.2s !important;
    margin-bottom: 4px !important;
}
[data-testid="stSidebar"] .stButton > button:hover {
    background: #1a3a5c !important;
    border-color: #4a90d9 !important;
    color: #ffffff !important;
}

/* ── Main Buttons ── */
.stButton > button {
    background: #0d2b4e !important;
    color: #ffffff !important;
    border: none !important;
    border-radius: 4px !important;
    font-size: 13px !important;
    font-weight: 600 !important;
    padding: 10px 28px !important;
    letter-spacing: 0.3px !important;
    transition: all 0.2s !important;
}
.stButton > button:hover {
    background: #1a4a7a !important;
    transform: translateY(-1px) !important;
    box-shadow: 0 4px 12px rgba(13,43,78,0.3) !important;
}

/* ── Tabs ── */
.stTabs [data-baseweb="tab-list"] {
    background: transparent;
    border-bottom: 2px solid #e2e8f0;
    gap: 0;
}
.stTabs [data-baseweb="tab"] {
    background: transparent !important;
    color: #64748b !important;
    font-size: 13px !important;
    font-weight: 500 !important;
    padding: 12px 24px !important;
    border: none !important;
    border-bottom: 2px solid transparent !important;
    margin-bottom: -2px !important;
}
.stTabs [aria-selected="true"] {
    color: #0d2b4e !important;
    border-bottom: 2px solid #0d2b4e !important;
    font-weight: 700 !important;
}

/* ── Cards ── */
.mck-card {
    background: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 8px;
    padding: 24px;
    margin: 8px 0;
    box-shadow: 0 1px 3px rgba(0,0,0,0.06);
}
.mck-card-blue {
    background: #0d2b4e;
    border-radius: 8px;
    padding: 24px;
    margin: 8px 0;
}
.mck-kpi-card {
    background: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 8px;
    padding: 20px 24px;
    margin: 4px 0;
    box-shadow: 0 1px 3px rgba(0,0,0,0.06);
    border-top: 3px solid #0d2b4e;
}
.mck-insight-card {
    background: #ffffff;
    border-left: 4px solid #0d2b4e;
    border-radius: 0 8px 8px 0;
    padding: 16px 20px;
    margin: 8px 0;
    box-shadow: 0 1px 3px rgba(0,0,0,0.06);
}
.mck-rec-card {
    background: #f8fafc;
    border: 1px solid #e2e8f0;
    border-radius: 8px;
    padding: 16px 20px;
    margin: 8px 0;
}
.mck-alarm-critical { border-left: 4px solid #dc2626; background: #fff5f5; border-radius: 0 8px 8px 0; padding: 12px 16px; margin: 6px 0; }
.mck-alarm-major    { border-left: 4px solid #d97706; background: #fffbeb; border-radius: 0 8px 8px 0; padding: 12px 16px; margin: 6px 0; }
.mck-alarm-minor    { border-left: 4px solid #6b7280; background: #f9fafb; border-radius: 0 8px 8px 0; padding: 12px 16px; margin: 6px 0; }

/* ── Typography ── */
.mck-page-title    { font-size: 28px; font-weight: 800; color: #0d2b4e; letter-spacing: -0.5px; margin: 0; }
.mck-page-subtitle { font-size: 14px; color: #64748b; font-weight: 400; margin-top: 4px; }
.mck-section-title { font-size: 11px; font-weight: 700; color: #94a3b8; letter-spacing: 1.5px; text-transform: uppercase; margin-bottom: 12px; }
.mck-card-title    { font-size: 15px; font-weight: 700; color: #0d2b4e; margin-bottom: 4px; }
.mck-card-body     { font-size: 13px; color: #475569; line-height: 1.7; }
.mck-kpi-value     { font-size: 32px; font-weight: 800; color: #0d2b4e; line-height: 1; }
.mck-kpi-label     { font-size: 11px; font-weight: 600; color: #94a3b8; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 8px; }
.mck-kpi-status-ok   { font-size: 12px; color: #16a34a; font-weight: 600; margin-top: 6px; }
.mck-kpi-status-warn { font-size: 12px; color: #d97706; font-weight: 600; margin-top: 6px; }
.mck-kpi-status-crit { font-size: 12px; color: #dc2626; font-weight: 600; margin-top: 6px; }

/* ── Badges ── */
.badge { display: inline-block; padding: 3px 12px; border-radius: 3px; font-size: 11px; font-weight: 700; letter-spacing: 0.8px; text-transform: uppercase; }
.badge-congestion   { background: #fef3c7; color: #92400e; border: 1px solid #fcd34d; }
.badge-bler         { background: #dbeafe; color: #1e40af; border: 1px solid #93c5fd; }
.badge-interference { background: #ede9fe; color: #5b21b6; border: 1px solid #c4b5fd; }
.badge-link_failure { background: #fee2e2; color: #991b1b; border: 1px solid #fca5a5; }
.badge-unknown      { background: #f1f5f9; color: #475569; border: 1px solid #cbd5e1; }
.badge-critical     { background: #fee2e2; color: #991b1b; }
.badge-major        { background: #fef3c7; color: #92400e; }
.badge-minor        { background: #f1f5f9; color: #475569; }

/* ── Confidence Bar ── */
.conf-track { background: #e2e8f0; border-radius: 4px; height: 6px; width: 100%; margin-top: 8px; }
.conf-fill  { height: 6px; border-radius: 4px; background: #0d2b4e; }

/* ── Divider ── */
hr { border-color: #e2e8f0 !important; margin: 16px 0 !important; }

/* ── Sidebar Logo Area ── */
.sidebar-logo {
    background: #0a2240;
    padding: 20px 16px 16px;
    margin: -16px -16px 16px;
    border-bottom: 1px solid #1e3d5c;
}
.sidebar-logo-title { font-size: 16px; font-weight: 800; color: #ffffff !important; letter-spacing: -0.3px; }
.sidebar-logo-sub   { font-size: 11px; color: #64a0c8 !important; margin-top: 2px; }

/* ── Status Dot ── */
.status-dot-green { display: inline-block; width: 8px; height: 8px; background: #22c55e; border-radius: 50%; margin-right: 6px; }
.status-dot-red   { display: inline-block; width: 8px; height: 8px; background: #ef4444; border-radius: 50%; margin-right: 6px; }

/* ── Text area & inputs ── */
.stTextArea textarea {
    border: 1px solid #e2e8f0 !important;
    border-radius: 6px !important;
    font-size: 13px !important;
    color: #1e293b !important;
    background: #ffffff !important;
}
.stTextArea textarea:focus {
    border-color: #0d2b4e !important;
    box-shadow: 0 0 0 2px rgba(13,43,78,0.1) !important;
}
.stSelectbox > div > div {
    border: 1px solid #e2e8f0 !important;
    border-radius: 6px !important;
    background: #ffffff !important;
}

/* ── Progress bar ── */
.stProgress > div > div { background: #0d2b4e !important; }

/* ── Metrics ── */
[data-testid="stMetric"] {
    background: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 8px;
    padding: 16px 20px;
    border-top: 3px solid #0d2b4e;
}
[data-testid="stMetricLabel"] { font-size: 11px !important; color: #94a3b8 !important; text-transform: uppercase; letter-spacing: 1px; font-weight: 600 !important; }
[data-testid="stMetricValue"] { font-size: 28px !important; font-weight: 800 !important; color: #0d2b4e !important; }

/* ── Expander ── */
.streamlit-expanderHeader { font-size: 13px !important; font-weight: 600 !important; color: #0d2b4e !important; padding-left: 8px !important; }
[data-testid="stExpander"] summary svg { display: none !important; }
[data-testid="stExpander"] details summary span { padding-left: 0 !important; }
[data-testid="stExpander"] summary::before { content: '' !important; display: none !important; }
[data-testid="stExpander"][open] summary::before { content: '' !important; display: none !important; }

/* ── Empty state ── */
.empty-state {
    text-align: center;
    padding: 60px 20px;
    background: #ffffff;
    border: 2px dashed #e2e8f0;
    border-radius: 8px;
}
</style>
""", unsafe_allow_html=True)

# ── Step 2a: Helpers + Session State ────────────────────────────────────────
API_URL = "http://localhost:8000"

def check_api():
    try:
        r = requests.get(f"{API_URL}/health", timeout=3)
        return r.status_code == 200
    except:
        return False

def call_analyze(query, cell_id, ne_id):
    r = requests.post(f"{API_URL}/analyze",
        json={"query": query, "cell_id": cell_id, "ne_id": ne_id},
        timeout=60)
    return r.json()

def load_kpis(cell_id):
    df = pd.read_csv("data/kpi_data.csv")
    return df[df["cell_id"] == cell_id].tail(10)

def load_alarms(ne_id):
    with open("data/alarms.json") as f:
        alarms = json.load(f)
    return [a for a in alarms if a["ne_id"] == ne_id]

def confidence_color(conf):
    if conf >= 0.8: return "#0d2b4e"
    if conf >= 0.6: return "#d97706"
    return "#dc2626"

def kpi_status(value, warn, crit, higher_is_bad=True):
    if higher_is_bad:
        if value >= crit: return "crit", "Critical"
        if value >= warn: return "warn", "Warning"
        return "ok", "Normal"
    else:
        if value <= crit: return "crit", "Critical"
        if value <= warn: return "warn", "Warning"
        return "ok", "Normal"

def badge_class(issue):
    mapping = {
        "congestion":     "badge-congestion",
        "bler_issue":     "badge-bler",
        "interference":   "badge-interference",
        "link_failure":   "badge-link_failure",
        "hardware_fault": "badge-congestion",
        "coverage_issue": "badge-interference",
        "healthy":        "badge-unknown",
    }
    return mapping.get(issue, "badge-unknown")

# Session State
if "history"     not in st.session_state: st.session_state.history     = []
if "last_result" not in st.session_state: st.session_state.last_result = None

# Pre-check API
api_ok = check_api()

# ── Step 2b: Sidebar Navigation ─────────────────────────────────────────────
with st.sidebar:

    # Logo Block
    st.markdown("""
    <div class="sidebar-logo">
        <div class="sidebar-logo-title">📡 Telecom AI Agent</div>
        <div class="sidebar-logo-sub">Root Cause Analysis Platform</div>
    </div>
    """, unsafe_allow_html=True)

    # API Status
    if api_ok:
        st.markdown('<p style="font-size:12px;color:#22c55e;font-weight:600;margin:0 0 8px;">⬤ &nbsp;API Connected</p>', unsafe_allow_html=True)
    else:
        st.markdown('<p style="font-size:12px;color:#ef4444;font-weight:600;margin:0 0 8px;">⬤ &nbsp;API Offline</p>', unsafe_allow_html=True)
        st.code("uvicorn app.main:app --reload --port 8000", language="bash")

    st.divider()

    # Network Element Selector
    st.markdown('<p style="font-size:11px;font-weight:700;color:#4a7fa5;letter-spacing:1.5px;text-transform:uppercase;margin-bottom:8px;">Network Element</p>', unsafe_allow_html=True)
    cell_id = st.selectbox("Cell ID", [f"CELL_{i:03d}" for i in range(1, 11)], label_visibility="collapsed")

    st.divider()

    # Quick Scenarios
    st.markdown('<p style="font-size:11px;font-weight:700;color:#4a7fa5;letter-spacing:1.5px;text-transform:uppercase;margin-bottom:8px;">Quick Scenarios</p>', unsafe_allow_html=True)
    scenarios = {
        "📉  Throughput Drop":  ("Throughput dropped after 5 minutes", "CELL_001"),
        "📶  High BLER":        ("High BLER issue detected",            "CELL_002"),
        "🔴  Cell Congestion":  ("Cell congestion detected",            "CELL_003"),
        "📡  Low SINR":         ("Low SINR and interference issue",     "CELL_005"),
        "🔗  Link Failure":     ("S1 link failure detected",            "CELL_007"),
    }
    for label, (query, cid) in scenarios.items():
        if st.button(label, key=f"q_{label}"):
            st.session_state["quick_query"] = query
            st.session_state["quick_cell"]  = cid
            st.rerun()

    st.divider()

    # Spectrum Efficiency Scenarios
    st.markdown('<p style="font-size:11px;font-weight:700;color:#4a7fa5;letter-spacing:1.5px;text-transform:uppercase;margin-bottom:8px;">📶 Spectrum Optimization</p>', unsafe_allow_html=True)

    spectrum_queries = {
        "📊  Spectrum Efficiency":  "Analyze spectrum efficiency: evaluate PRB utilization, throughput per PRB, BLER impact on spectral efficiency, and SINR distribution. Identify underutilized and over-utilized spectrum resources and recommend optimization actions.",
        "🔧  PRB Optimization":     "Analyze PRB utilization patterns and recommend optimal PRB allocation strategy to maximize throughput while minimizing interference and congestion.",
        "🌐  Frequency Planning":   "Evaluate current frequency usage, identify inter-cell interference patterns, and recommend frequency reuse optimization to improve overall network spectral efficiency.",
        "⚡  Capacity Planning":    "Analyze current cell capacity utilization including PRB usage, RRC connections, throughput demand, and recommend capacity expansion or load balancing strategies.",
    }
    for label, sq in spectrum_queries.items():
        if st.button(label, key=f"spec_{label}"):
            st.session_state["quick_query"] = sq
            st.session_state["quick_cell"]  = cell_id
            st.session_state["spectrum_mode"] = True
            st.rerun()

    st.divider()

    # Multi-cell Spectrum Scan
    st.markdown('<p style="font-size:11px;font-weight:700;color:#4a7fa5;letter-spacing:1.5px;text-transform:uppercase;margin-bottom:8px;">🚀 Network-Wide Scan</p>', unsafe_allow_html=True)
    all_cells_list = [f"CELL_{i:03d}" for i in range(1, 11)]
    scan_type = st.selectbox("Scan Type", [
        "Spectrum Efficiency Audit",
        "PRB Optimization Scan",
        "Interference Detection",
        "Capacity Health Check",
        "Full Network Diagnostics",
    ], label_visibility="collapsed")

    scan_queries = {
        "Spectrum Efficiency Audit":  "Analyze spectrum efficiency for this cell: evaluate PRB utilization vs throughput ratio, spectral efficiency in bps/Hz, BLER impact, and SINR quality. Provide optimization recommendations.",
        "PRB Optimization Scan":      "Analyze PRB allocation and utilization for this cell. Identify wasted PRBs, over-allocated resources, and recommend optimal PRB scheduling to maximize spectral efficiency.",
        "Interference Detection":     "Detect and analyze interference patterns for this cell. Evaluate SINR degradation, BLER correlation, and identify potential interference sources. Recommend mitigation strategies.",
        "Capacity Health Check":      "Perform capacity health check for this cell. Analyze RRC connections, PRB utilization, throughput demand, latency, and recommend capacity optimization or expansion.",
        "Full Network Diagnostics":   "Run full diagnostics for this cell: analyze all KPIs including throughput, PRB utilization, BLER, SINR, latency, RRC connections. Identify all issues and provide comprehensive optimization plan.",
    }

    sidebar_cells = st.multiselect("Select Cells", all_cells_list, default=[], placeholder="Pick cells...",
                                    label_visibility="collapsed", key="sidebar_multi")
    sidebar_all = st.checkbox("✅ Select All 10 Cells", key="sidebar_all")
    if sidebar_all:
        sidebar_cells = all_cells_list

    if st.button("🚀  Run Network Scan", key="network_scan"):
        if sidebar_cells:
            st.session_state["batch_scan_query"] = scan_queries[scan_type]
            st.session_state["batch_scan_cells"] = sidebar_cells
            st.session_state["batch_scan_type"]  = scan_type
            st.rerun()
        else:
            st.markdown('<p style="font-size:11px;color:#ef4444;">Select at least one cell</p>', unsafe_allow_html=True)

    st.divider()

    # Session Summary
    st.markdown('<p style="font-size:11px;font-weight:700;color:#4a7fa5;letter-spacing:1.5px;text-transform:uppercase;margin-bottom:8px;">Session Summary</p>', unsafe_allow_html=True)
    total = len(st.session_state.history)
    st.markdown(f"""
    <div style="margin-bottom:6px;">
        <div style="display:flex;justify-content:space-between;padding:6px 0;border-bottom:1px solid #1e3d5c;">
            <span style="font-size:12px;color:#94a3b8;">Total Analyses</span>
            <span style="font-size:12px;font-weight:700;color:#ffffff;">{total}</span>
        </div>
    """, unsafe_allow_html=True)

    if st.session_state.history:
        avg_conf = sum(h["confidence"] for h in st.session_state.history) / total
        issues   = [h["issue_type"] for h in st.session_state.history]
        top_issue = max(set(issues), key=issues.count).replace("_"," ").title()
        st.markdown(f"""
        <div style="display:flex;justify-content:space-between;padding:6px 0;border-bottom:1px solid #1e3d5c;">
            <span style="font-size:12px;color:#94a3b8;">Avg Confidence</span>
            <span style="font-size:12px;font-weight:700;color:#22c55e;">{avg_conf*100:.0f}%</span>
        </div>
        <div style="display:flex;justify-content:space-between;padding:6px 0;">
            <span style="font-size:12px;color:#94a3b8;">Top Issue</span>
            <span style="font-size:12px;font-weight:700;color:#f59e0b;">{top_issue}</span>
        </div>
        """, unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)
    st.divider()

    if st.button("↺  Reset Session"):
        st.session_state.history     = []
        st.session_state.last_result = None
        st.rerun()

    # Footer
    st.markdown("""
    <div style="margin-top:32px;padding-top:16px;border-top:1px solid #1e3d5c;">
        <p style="font-size:10px;color:#2d5a8e;text-align:center;line-height:1.6;">
            Powered by LangGraph + OpenAI<br>
            © 2024 Telecom AI Platform
        </p>
    </div>
    """, unsafe_allow_html=True)

# ── Step 2c: Executive Header ────────────────────────────────────────────────
now = datetime.now().strftime("%d %b %Y  ·  %H:%M")

col_title, col_status = st.columns([3, 1])

with col_title:
    st.markdown("""
    <div style="padding:12px 0 8px;">
        <div class="mck-page-title">Telecom Network Intelligence</div>
        <div class="mck-page-subtitle">
            AI-powered Root Cause Analysis &nbsp;·&nbsp; LangGraph Agent Workflow &nbsp;·&nbsp; Real-time KPI Monitoring
        </div>
    </div>
    """, unsafe_allow_html=True)

with col_status:
    status_color = "#16a34a" if api_ok else "#dc2626"
    status_text  = "System Operational" if api_ok else "System Offline"
    status_dot   = "#22c55e" if api_ok else "#ef4444"
    st.markdown(f"""
    <div style="text-align:right;padding-top:16px;">
        <div style="font-size:11px;color:#94a3b8;font-weight:500;">{now}</div>
        <div style="margin-top:6px;display:inline-flex;align-items:center;gap:6px;
                    background:#ffffff;border:1px solid #e2e8f0;border-radius:20px;
                    padding:4px 12px;box-shadow:0 1px 3px rgba(0,0,0,0.06);">
            <span style="width:7px;height:7px;background:{status_dot};
                         border-radius:50%;display:inline-block;"></span>
            <span style="font-size:11px;font-weight:600;color:{status_color};">{status_text}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

# Accent divider line
st.markdown('<hr style="border:none;border-top:2px solid #0d2b4e;margin:4px 0 20px 0;">', unsafe_allow_html=True)

# Executive KPI summary bar (top-level metrics)
if st.session_state.history:
    total    = len(st.session_state.history)
    avg_conf = sum(h["confidence"] for h in st.session_state.history) / total
    issues   = [h["issue_type"] for h in st.session_state.history]
    top_issue = max(set(issues), key=issues.count).replace("_"," ").title()
    cells    = len(set(h["cell_id"] for h in st.session_state.history))

    b1, b2, b3, b4 = st.columns(4)
    with b1: st.metric("Total Analyses",  total)
    with b2: st.metric("Avg Confidence",  f"{avg_conf*100:.0f}%")
    with b3: st.metric("Top Issue Type",  top_issue)
    with b4: st.metric("Cells Analysed",  cells)
    st.markdown("<div style='margin-bottom:16px;'></div>", unsafe_allow_html=True)

# Main tabs
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "🔍  Analyze",
    "📊  KPI Monitor",
    "⚠️  Anomaly Detection",
    "⚙️  Config Audit",
    "📡  Real-Time Analytics",
    "📜  History"
])

# ── Step 3a: Analyze Tab — Query Input ──────────────────────────────────────
with tab1:
    col_left, col_right = st.columns([1, 1], gap="large")

    with col_left:
        # Section title
        st.markdown('<p class="mck-section-title">Query Input</p>', unsafe_allow_html=True)

        # Pre-fill from quick buttons
        default_query = st.session_state.get("quick_query", "")
        default_cell  = st.session_state.get("quick_cell",  cell_id)

        # White card wrapper
        st.markdown('<div class="mck-card">', unsafe_allow_html=True)

        query = st.text_area(
            "Describe the network issue",
            value=default_query,
            height=130,
            placeholder="e.g. Throughput dropped after 5 minutes on CELL_001...",
            label_visibility="collapsed"
        )

        c1, c2 = st.columns(2)
        with c1:
            cells_list    = [f"CELL_{i:03d}" for i in range(1, 11)]
            default_index = cells_list.index(default_cell) if default_cell in cells_list else 0
            selected_cell = st.selectbox("Cell ID", cells_list, index=default_index, key="analyze_cell")
        with c2:
            st.text_input("NE ID", value=selected_cell, disabled=True)

        # Multi-cell selection
        st.markdown('<p style="font-size:11px;font-weight:600;color:#94a3b8;margin:12px 0 4px;text-transform:uppercase;letter-spacing:1px;">Or select multiple cells</p>', unsafe_allow_html=True)
        mc1, mc2 = st.columns([3, 1])
        with mc1:
            multi_cells = st.multiselect("Select multiple cells",
                                          cells_list,
                                          default=[],
                                          placeholder="Pick cells for batch analysis...",
                                          label_visibility="collapsed")
        with mc2:
            if st.checkbox("All", key="select_all_main"):
                multi_cells = cells_list

        st.markdown('</div>', unsafe_allow_html=True)

        # Workflow steps visual
        st.markdown("""
        <div style="margin:16px 0 12px;">
            <p class="mck-section-title">Agent Workflow</p>
            <div style="display:flex;align-items:center;gap:0;margin-top:8px;">
                <div style="background:#0d2b4e;color:#fff;font-size:10px;font-weight:700;
                            padding:6px 10px;border-radius:4px 0 0 4px;letter-spacing:0.5px;">CLASSIFY</div>
                <div style="width:20px;height:2px;background:#cbd5e1;"></div>
                <div style="background:#1a4a7a;color:#fff;font-size:10px;font-weight:700;
                            padding:6px 10px;letter-spacing:0.5px;">RETRIEVE</div>
                <div style="width:20px;height:2px;background:#cbd5e1;"></div>
                <div style="background:#1a4a7a;color:#fff;font-size:10px;font-weight:700;
                            padding:6px 10px;letter-spacing:0.5px;">ANALYZE</div>
                <div style="width:20px;height:2px;background:#cbd5e1;"></div>
                <div style="background:#1a4a7a;color:#fff;font-size:10px;font-weight:700;
                            padding:6px 10px;letter-spacing:0.5px;">RECOMMEND</div>
                <div style="width:20px;height:2px;background:#cbd5e1;"></div>
                <div style="background:#16a34a;color:#fff;font-size:10px;font-weight:700;
                            padding:6px 10px;border-radius:0 4px 4px 0;letter-spacing:0.5px;">VALIDATE</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Run button + auto-submit logic
        auto_submit = "quick_query" in st.session_state
        btn_col1, btn_col2 = st.columns(2)
        with btn_col1:
            analyze_btn = st.button("🔍  Run Analysis", type="primary", disabled=not api_ok)
        with btn_col2:
            batch_btn = st.button("🚀  Run All Selected", disabled=not api_ok or len(multi_cells) == 0)

        # Single cell analysis
        if (analyze_btn or auto_submit) and query.strip():
            with st.spinner(""):
                progress = st.progress(0)
                steps = [
                    (25,  "Classifying issue type..."),
                    (50,  "Retrieving KPI, alarm & log data..."),
                    (75,  "Analyzing root cause..."),
                    (95,  "Generating recommendations..."),
                ]
                for pct, msg in steps:
                    st.markdown(f'<p style="font-size:12px;color:#64748b;margin:4px 0;">⚙️ &nbsp;{msg}</p>', unsafe_allow_html=True)
                    time.sleep(0.3)
                    progress.progress(pct)
                try:
                    result = call_analyze(query, selected_cell, selected_cell)
                    result["query"]     = query
                    result["timestamp"] = datetime.now().strftime("%H:%M:%S")
                    st.session_state.last_result = result
                    st.session_state.history.append(result)
                    st.session_state.pop("quick_query", None)
                    st.session_state.pop("quick_cell",  None)
                    progress.progress(100)
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ Error: {e}")

        # Multi-cell batch analysis
        if batch_btn and query.strip() and multi_cells:
            st.markdown('<hr style="border:none;border-top:1px solid #e2e8f0;margin:16px 0;">', unsafe_allow_html=True)
            st.markdown(f'<p class="mck-section-title">🚀 Batch Analysis — {len(multi_cells)} Cells</p>', unsafe_allow_html=True)
            batch_progress = st.progress(0)
            batch_results  = []

            for idx, cid in enumerate(multi_cells):
                st.markdown(f'<p style="font-size:12px;color:#64748b;margin:2px 0;">⚙️ Analyzing {cid}...</p>', unsafe_allow_html=True)
                try:
                    r = call_analyze(query, cid, cid)
                    r["query"]     = query
                    r["timestamp"] = datetime.now().strftime("%H:%M:%S")
                    batch_results.append(r)
                    st.session_state.history.append(r)
                except Exception as e:
                    batch_results.append({"cell_id": cid, "issue_type": "error",
                                          "analysis": str(e), "recommendation": "", "confidence": 0})
                batch_progress.progress(int((idx + 1) / len(multi_cells) * 100))

            # Batch summary table
            st.markdown('<p class="mck-section-title" style="margin-top:16px;">Batch Summary</p>', unsafe_allow_html=True)
            summary = pd.DataFrame([{
                "Cell":       r.get("cell_id", ""),
                "Issue Type": r.get("issue_type", "").replace("_", " ").title(),
                "Confidence": f"{r.get('confidence', 0)*100:.0f}%",
                "Analysis":   r.get("analysis", "")[:80] + "...",
            } for r in batch_results])
            st.dataframe(summary, width="stretch", hide_index=True)

            # Batch detail cards
            for r in batch_results:
                issue_r  = r.get("issue_type", "unknown")
                bclass_r = badge_class(issue_r)
                conf_r   = r.get("confidence", 0)
                st.markdown(f"""
                <div class="mck-card" style="margin:8px 0;padding:16px 20px;">
                    <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:8px;">
                        <div style="display:flex;align-items:center;gap:10px;">
                            <span class="badge {bclass_r}">{issue_r.replace("_"," ").upper()}</span>
                            <span style="font-size:12px;font-weight:700;color:#0d2b4e;">{r.get('cell_id','')}</span>
                        </div>
                        <span style="font-size:12px;font-weight:700;color:#0d2b4e;">{conf_r*100:.0f}%</span>
                    </div>
                    <div style="font-size:12px;color:#64748b;line-height:1.6;">{r.get('analysis','')[:200]}...</div>
                </div>
                """, unsafe_allow_html=True)

            st.session_state.last_result = batch_results[-1] if batch_results else None

        # ── Network-Wide Scan Execution ────────────────────────────────────────
        if "batch_scan_query" in st.session_state:
            scan_q     = st.session_state.pop("batch_scan_query")
            scan_cells = st.session_state.pop("batch_scan_cells")
            scan_type  = st.session_state.pop("batch_scan_type")

            st.markdown('<hr style="border:none;border-top:2px solid #0d2b4e;margin:24px 0 16px;">', unsafe_allow_html=True)
            st.markdown(f"""
            <div class="mck-card-blue" style="margin-bottom:16px;">
                <div style="font-size:11px;font-weight:700;color:#64a0c8;letter-spacing:1.5px;text-transform:uppercase;">🚀 Network-Wide Scan</div>
                <div style="font-size:18px;font-weight:800;color:#ffffff;margin-top:6px;">{scan_type}</div>
                <div style="font-size:12px;color:#94b8d4;margin-top:4px;">{len(scan_cells)} cells selected · Running analysis...</div>
            </div>
            """, unsafe_allow_html=True)

            scan_progress = st.progress(0)
            scan_results  = []

            for idx, cid in enumerate(scan_cells):
                st.markdown(f'<p style="font-size:12px;color:#64748b;margin:2px 0;">⚙️ Scanning {cid} ({idx+1}/{len(scan_cells)})...</p>', unsafe_allow_html=True)
                try:
                    r = call_analyze(scan_q, cid, cid)
                    r["query"]     = f"[{scan_type}] {cid}"
                    r["timestamp"] = datetime.now().strftime("%H:%M:%S")
                    scan_results.append(r)
                    st.session_state.history.append(r)
                except Exception as e:
                    scan_results.append({"cell_id": cid, "issue_type": "error",
                                          "analysis": str(e), "recommendation": "", "confidence": 0})
                scan_progress.progress(int((idx + 1) / len(scan_cells) * 100))

            # Executive Summary
            st.markdown('<p class="mck-section-title" style="margin-top:20px;">Executive Summary</p>', unsafe_allow_html=True)

            total_cells = len(scan_results)
            avg_conf    = sum(r.get("confidence", 0) for r in scan_results) / max(total_cells, 1)
            issues_found = [r.get("issue_type", "") for r in scan_results if r.get("issue_type") not in ["", "unknown", "error"]]
            issue_counts = {}
            for iss in issues_found:
                issue_counts[iss] = issue_counts.get(iss, 0) + 1
            critical_cells = [r.get("cell_id") for r in scan_results if r.get("confidence", 0) >= 0.85]

            s1, s2, s3, s4 = st.columns(4)
            with s1: st.metric("Cells Scanned", total_cells)
            with s2: st.metric("Avg Confidence", f"{avg_conf*100:.0f}%")
            with s3: st.metric("Issues Found", len(issues_found))
            with s4: st.metric("Critical Cells", len(critical_cells))

            # Issue Distribution
            if issue_counts:
                st.markdown('<p class="mck-section-title" style="margin-top:16px;">Issue Distribution</p>', unsafe_allow_html=True)
                dist_cols = st.columns(len(issue_counts))
                for i, (iss, cnt) in enumerate(sorted(issue_counts.items(), key=lambda x: -x[1])):
                    bclass_i = badge_class(iss)
                    with dist_cols[i]:
                        st.markdown(f"""
                        <div class="mck-kpi-card" style="text-align:center;">
                            <div class="mck-kpi-value">{cnt}</div>
                            <div style="margin-top:8px;"><span class="badge {bclass_i}">{iss.replace("_"," ").upper()}</span></div>
                        </div>
                        """, unsafe_allow_html=True)

            # Results Table
            st.markdown('<p class="mck-section-title" style="margin-top:16px;">Cell-by-Cell Results</p>', unsafe_allow_html=True)
            scan_df = pd.DataFrame([{
                "Cell":       r.get("cell_id", ""),
                "Issue Type": r.get("issue_type", "").replace("_", " ").title(),
                "Confidence": f"{r.get('confidence', 0)*100:.0f}%",
                "Key Finding": r.get("analysis", "")[:100] + "...",
            } for r in scan_results])
            st.dataframe(scan_df, width="stretch", hide_index=True)

            # Detailed Findings — clean cards, no expanders
            st.markdown('<p class="mck-section-title" style="margin-top:16px;">Detailed Findings</p>', unsafe_allow_html=True)
            for r in scan_results:
                issue_r  = r.get("issue_type", "unknown")
                bclass_r = badge_class(issue_r)
                conf_r   = r.get("confidence", 0)
                analysis_r = r.get("analysis", "")
                recs_r     = r.get("recommendation", "").replace("**", "")

                st.markdown(f"""
                <div class="mck-card" style="margin:12px 0;padding:20px 24px;">
                    <div style="display:flex;align-items:center;justify-content:space-between;
                                padding-bottom:12px;margin-bottom:12px;border-bottom:1px solid #e2e8f0;">
                        <div style="display:flex;align-items:center;gap:10px;">
                            <span class="badge {bclass_r}">{issue_r.replace("_"," ").upper()}</span>
                            <span style="font-size:13px;font-weight:700;color:#0d2b4e;">{r.get('cell_id','')}</span>
                        </div>
                        <span style="font-size:16px;font-weight:800;color:#0d2b4e;">{conf_r*100:.0f}%</span>
                    </div>
                    <div style="margin-bottom:12px;">
                        <div style="font-size:11px;font-weight:700;color:#94a3b8;text-transform:uppercase;
                                    letter-spacing:1px;margin-bottom:6px;">Root Cause Analysis</div>
                        <div class="mck-card-body">{analysis_r}</div>
                    </div>
                    <div>
                        <div style="font-size:11px;font-weight:700;color:#94a3b8;text-transform:uppercase;
                                    letter-spacing:1px;margin-bottom:6px;">Recommendations</div>
                        <div class="mck-card-body" style="white-space:pre-line;">{recs_r}</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

            st.session_state.last_result = scan_results[-1] if scan_results else None

    # ── Step 3b: Results Panel ───────────────────────────────────────────────────
    with col_right:
        st.markdown('<p class="mck-section-title">Analysis Results</p>', unsafe_allow_html=True)

        result = st.session_state.last_result

        if not result:
            st.markdown("""
            <div class="empty-state">
                <div style="font-size:40px;margin-bottom:12px;">📡</div>
                <div style="font-size:15px;font-weight:700;color:#0d2b4e;margin-bottom:6px;">No Analysis Yet</div>
                <div style="font-size:13px;color:#94a3b8;">
                    Select a quick scenario or enter a custom query<br>and click Run Analysis
                </div>
            </div>
            """, unsafe_allow_html=True)
        else:
            issue      = result.get("issue_type", "unknown")
            conf       = result.get("confidence", 0)
            analysis   = result.get("analysis", "")
            recs       = result.get("recommendation", "")
            cell       = result.get("cell_id", "")
            ts         = result.get("timestamp", "")
            bclass     = badge_class(issue)
            bar_color  = confidence_color(conf)

            # ── Header row: badge + meta
            st.markdown(f"""
            <div style="display:flex;align-items:center;justify-content:space-between;
                        margin-bottom:16px;padding-bottom:12px;border-bottom:1px solid #e2e8f0;">
                <span class="badge {bclass}">{issue.replace("_"," ").upper()}</span>
                <span style="font-size:11px;color:#94a3b8;font-weight:500;">
                    {cell} &nbsp;·&nbsp; {ts}
                </span>
            </div>
            """, unsafe_allow_html=True)

            # ── Confidence scorecard
            st.markdown(f"""
            <div class="mck-kpi-card" style="margin-bottom:16px;">
                <div class="mck-kpi-label">Confidence Score</div>
                <div style="display:flex;align-items:flex-end;gap:16px;">
                    <div style="font-size:36px;font-weight:800;color:{bar_color};line-height:1;">
                        {conf*100:.0f}%
                    </div>
                    <div style="flex:1;padding-bottom:6px;">
                        <div style="display:flex;justify-content:space-between;margin-bottom:4px;">
                            <span style="font-size:11px;color:#94a3b8;">Low</span>
                            <span style="font-size:11px;color:#94a3b8;">High</span>
                        </div>
                        <div class="conf-track">
                            <div class="conf-fill" style="width:{conf*100}%;background:{bar_color};"></div>
                        </div>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

            # ── Root Cause Analysis
            st.markdown('<p class="mck-section-title" style="margin-top:16px;">Root Cause Analysis</p>', unsafe_allow_html=True)
            st.markdown(f"""
            <div class="mck-insight-card">
                <div class="mck-card-title">Key Finding</div>
                <div class="mck-card-body" style="margin-top:8px;">{analysis}</div>
            </div>
            """, unsafe_allow_html=True)

            # ── Recommendations
            st.markdown('<p class="mck-section-title" style="margin-top:16px;">Recommended Actions</p>', unsafe_allow_html=True)
            rec_lines = [l.strip() for l in recs.split("\n") if l.strip()]
            rec_num   = 0
            for line in rec_lines:
                if line and (line[0].isdigit() or line.startswith("-") or line.startswith("*")):
                    rec_num += 1
                    clean = line.lstrip("0123456789.-* ").strip()
                    st.markdown(f"""
                    <div class="mck-rec-card">
                        <div style="display:flex;gap:12px;align-items:flex-start;">
                            <div style="min-width:24px;height:24px;background:#0d2b4e;color:#fff;
                                        border-radius:50%;display:flex;align-items:center;
                                        justify-content:center;font-size:11px;font-weight:700;
                                        margin-top:1px;">{rec_num}</div>
                            <div class="mck-card-body">{clean}</div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                elif line and rec_num > 0:
                    st.markdown(f"""
                    <div style="padding:4px 0 4px 36px;">
                        <div class="mck-card-body">{line}</div>
                    </div>
                    """, unsafe_allow_html=True)

    # ── Step 3c: Chat History ──────────────────────────────────────────────────
    if st.session_state.history:
        st.markdown('<hr style="border:none;border-top:1px solid #e2e8f0;margin:24px 0 16px;">', unsafe_allow_html=True)
        st.markdown('<p class="mck-section-title">Recent Analyses</p>', unsafe_allow_html=True)

        for h in reversed(st.session_state.history[-4:]):
            issue_h  = h.get("issue_type", "unknown")
            conf_h   = h.get("confidence", 0)
            query_h  = h.get("query", "")
            cell_h   = h.get("cell_id", "")
            ts_h     = h.get("timestamp", "")
            analysis_h = h.get("analysis", "")[:180]
            bclass_h = badge_class(issue_h)

            st.markdown(f"""
            <div class="mck-card" style="margin:8px 0;padding:16px 20px;">
                <!-- Header row -->
                <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:10px;">
                    <div style="display:flex;align-items:center;gap:10px;">
                        <span class="badge {bclass_h}">{issue_h.replace("_"," ").upper()}</span>
                        <span style="font-size:11px;color:#94a3b8;">{cell_h} &nbsp;·&nbsp; {ts_h}</span>
                    </div>
                    <span style="font-size:12px;font-weight:700;color:#0d2b4e;">{conf_h*100:.0f}% confidence</span>
                </div>
                <!-- Query -->
                <div style="background:#f8fafc;border-radius:6px;padding:8px 12px;margin-bottom:8px;">
                    <span style="font-size:11px;font-weight:600;color:#94a3b8;text-transform:uppercase;
                                 letter-spacing:0.8px;">Query &nbsp;</span>
                    <span style="font-size:13px;color:#1e293b;">{query_h}</span>
                </div>
                <!-- Analysis snippet -->
                <div style="font-size:12px;color:#64748b;line-height:1.6;">
                    {analysis_h}{'...' if len(h.get('analysis','')) > 180 else ''}
                </div>
            </div>
            """, unsafe_allow_html=True)

# ══ Step 4a + 4b: KPI Monitor Tab ═══════════════════════════════════════════
with tab2:
    st.markdown('<p class="mck-section-title">KPI Monitor</p>', unsafe_allow_html=True)

    mon_c1, mon_c2 = st.columns([2, 5])
    with mon_c1:
        monitor_cell = st.selectbox("Select Cell", [f"CELL_{i:03d}" for i in range(1, 11)], key="monitor_cell")

    try:
        df = load_kpis(monitor_cell)
        latest = df.iloc[-1]

        prb  = latest["prb_utilization"]
        tput = latest["throughput_mbps"]
        bler = latest["bler_pct"]
        sinr = latest["sinr_db"]
        rrc  = latest["rrc_connected"]
        lat  = latest["latency_ms"]

        prb_s,  prb_l  = kpi_status(prb,  70, 85)
        tput_s, tput_l = kpi_status(tput, 30, 15, higher_is_bad=False)
        bler_s, bler_l = kpi_status(bler,  5, 10)
        sinr_s, sinr_l = kpi_status(sinr,  5,  0, higher_is_bad=False)
        rrc_s,  rrc_l  = kpi_status(rrc, 150, 220)
        lat_s,  lat_l  = kpi_status(lat,  40,  80)

        def kpi_bar_color(s):
            return "#dc2626" if s == "crit" else "#d97706" if s == "warn" else "#0d2b4e"

        def render_kpi(label, value, unit, status_s, status_l, fill_pct):
            return f"""
            <div class="mck-kpi-card">
                <div class="mck-kpi-label">{label}</div>
                <div class="mck-kpi-value">{value} <span style="font-size:14px;font-weight:500;">{unit}</span></div>
                <div class="mck-kpi-status-{status_s}">{status_l}</div>
                <div style="margin-top:10px;"><div class="conf-track">
                    <div class="conf-fill" style="width:{min(fill_pct,100):.0f}%;background:{kpi_bar_color(status_s)};"></div>
                </div></div>
            </div>"""

        # Row 1
        k1, k2, k3 = st.columns(3)
        with k1: st.markdown(render_kpi("PRB Utilization", f"{prb:.1f}", "%", prb_s, prb_l, prb), unsafe_allow_html=True)
        with k2: st.markdown(render_kpi("DL Throughput", f"{tput:.1f}", "Mbps", tput_s, tput_l, tput/150*100), unsafe_allow_html=True)
        with k3: st.markdown(render_kpi("BLER", f"{bler:.1f}", "%", bler_s, bler_l, bler*5), unsafe_allow_html=True)

        # Row 2
        k4, k5, k6 = st.columns(3)
        with k4: st.markdown(render_kpi("SINR", f"{sinr:.1f}", "dB", sinr_s, sinr_l, max((sinr+5)/30*100, 0)), unsafe_allow_html=True)
        with k5: st.markdown(render_kpi("RRC Connected", f"{int(rrc)}", "", rrc_s, rrc_l, rrc/300*100), unsafe_allow_html=True)
        with k6: st.markdown(render_kpi("Latency", f"{lat:.0f}", "ms", lat_s, lat_l, lat/200*100), unsafe_allow_html=True)

        # Step 4b: Charts
        st.markdown('<hr style="border:none;border-top:1px solid #e2e8f0;margin:20px 0;">', unsafe_allow_html=True)
        st.markdown('<p class="mck-section-title">Trend Analysis</p>', unsafe_allow_html=True)

        ch1, ch2 = st.columns(2)
        with ch1:
            st.markdown('<div class="mck-card"><div class="mck-card-title">Throughput & PRB Trend</div>', unsafe_allow_html=True)
            chart_df = df[["timestamp", "throughput_mbps", "prb_utilization"]].copy()
            chart_df["timestamp"] = pd.to_datetime(chart_df["timestamp"])
            chart_df = chart_df.set_index("timestamp")
            st.line_chart(chart_df, color=["#0d2b4e", "#d97706"])
            st.markdown('</div>', unsafe_allow_html=True)

        with ch2:
            st.markdown('<div class="mck-card"><div class="mck-card-title">BLER & Retransmission Trend</div>', unsafe_allow_html=True)
            chart_df2 = df[["timestamp", "bler_pct", "retx_rate_pct"]].copy()
            chart_df2["timestamp"] = pd.to_datetime(chart_df2["timestamp"])
            chart_df2 = chart_df2.set_index("timestamp")
            st.line_chart(chart_df2, color=["#dc2626", "#7c3aed"])
            st.markdown('</div>', unsafe_allow_html=True)

        # Alarms
        st.markdown('<hr style="border:none;border-top:1px solid #e2e8f0;margin:20px 0;">', unsafe_allow_html=True)
        st.markdown('<p class="mck-section-title">Active Alarms</p>', unsafe_allow_html=True)
        alarms = load_alarms(monitor_cell)
        if alarms:
            for alarm in alarms:
                sev = alarm["severity"]
                css_class = {"CRITICAL": "mck-alarm-critical", "MAJOR": "mck-alarm-major"}.get(sev, "mck-alarm-minor")
                sev_color = {"CRITICAL": "#dc2626", "MAJOR": "#d97706"}.get(sev, "#6b7280")
                st.markdown(f"""
                <div class="{css_class}">
                    <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:4px;">
                        <div>
                            <span style="font-size:11px;font-weight:700;color:{sev_color};">{sev}</span>
                            <span style="font-size:12px;color:#475569;margin-left:8px;font-weight:600;">{alarm['alarm_type']}</span>
                        </div>
                        <span style="font-size:11px;color:#94a3b8;">{alarm['timestamp']}</span>
                    </div>
                    <div style="font-size:12px;color:#64748b;">{alarm['description']}</div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="mck-card" style="text-align:center;padding:24px;">
                <span style="font-size:13px;color:#16a34a;font-weight:600;">✅ No active alarms for {monitor_cell}</span>
            </div>
            """, unsafe_allow_html=True)

        # Raw data
        with st.expander("📋 Raw KPI Data"):
            st.dataframe(df.style.background_gradient(cmap="Blues"), width="stretch")

    except Exception as e:
        st.error(f"Error loading KPI data: {e}")

# ══ Tab 3: Anomaly Detection ═══════════════════════════════════════════════
with tab3:
    st.markdown('<p class="mck-section-title">Anomaly Detection</p>', unsafe_allow_html=True)

    ad_c1, ad_c2 = st.columns([2, 5])
    with ad_c1:
        ad_cell = st.selectbox("Select Cell", [f"CELL_{i:03d}" for i in range(1, 11)], key="anomaly_cell")

    try:
        ad_result = requests.get(f"{API_URL}/anomaly/{ad_cell}", timeout=30).json()

        if "error" in ad_result:
            st.error(ad_result["error"])
        else:
            # Health score header
            score = ad_result.get("health_score", 0)
            status = ad_result.get("health_status", "")
            score_color = "#16a34a" if score >= 80 else ("#d97706" if score >= 50 else "#dc2626")
            status_label = "HEALTHY" if score >= 80 else ("DEGRADED" if score >= 50 else "CRITICAL")

            st.markdown(f"""
            <div class="mck-card-blue" style="margin-bottom:16px;">
                <div style="display:flex;align-items:center;justify-content:space-between;">
                    <div>
                        <div style="font-size:11px;font-weight:700;color:#64a0c8;letter-spacing:1.5px;
                                    text-transform:uppercase;">Cell Health Score</div>
                        <div style="font-size:42px;font-weight:800;color:#ffffff;margin-top:4px;">{score}</div>
                        <div style="font-size:12px;color:{score_color};font-weight:700;margin-top:4px;">{status_label}</div>
                    </div>
                    <div style="text-align:right;">
                        <div style="font-size:11px;color:#94b8d4;">Anomalies Found</div>
                        <div style="font-size:28px;font-weight:800;color:#ffffff;">{ad_result.get('anomaly_count',0)}</div>
                        <div style="font-size:11px;color:#ef4444;font-weight:600;">
                            {ad_result.get('critical_count',0)} Critical · {ad_result.get('warning_count',0)} Warning
                        </div>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

            # KPI Summary Cards
            st.markdown('<p class="mck-section-title">KPI Health Summary</p>', unsafe_allow_html=True)
            kpi_summary = ad_result.get("kpi_summary", {})
            kpi_items = list(kpi_summary.values())

            # Row 1
            if len(kpi_items) >= 3:
                r1, r2, r3 = st.columns(3)
                for col, kpi in zip([r1, r2, r3], kpi_items[:3]):
                    sev = kpi.get("severity", "normal")
                    sev_color = "#dc2626" if sev == "critical" else ("#d97706" if sev == "warning" else "#16a34a")
                    trend = kpi.get("trend", "stable")
                    trend_icon = "↑" if trend == "degrading" else ("↓" if trend == "improving" else "→")
                    trend_color = "#dc2626" if trend == "degrading" else ("#16a34a" if trend == "improving" else "#94a3b8")
                    with col:
                        st.markdown(f"""
                        <div class="mck-kpi-card">
                            <div class="mck-kpi-label">{kpi['kpi'].replace('_',' ').title()}</div>
                            <div class="mck-kpi-value">{kpi['latest_value']} <span style="font-size:14px;">{kpi['unit']}</span></div>
                            <div style="display:flex;justify-content:space-between;margin-top:8px;">
                                <span style="font-size:11px;color:{sev_color};font-weight:600;">{sev.upper()}</span>
                                <span style="font-size:11px;color:{trend_color};font-weight:600;">{trend_icon} {trend.title()}</span>
                            </div>
                            <div style="font-size:10px;color:#94a3b8;margin-top:4px;">Mean: {kpi['mean']} | Z-score: {kpi['z_score']}</div>
                        </div>
                        """, unsafe_allow_html=True)

            # Row 2
            if len(kpi_items) >= 6:
                r4, r5, r6 = st.columns(3)
                for col, kpi in zip([r4, r5, r6], kpi_items[3:6]):
                    sev = kpi.get("severity", "normal")
                    sev_color = "#dc2626" if sev == "critical" else ("#d97706" if sev == "warning" else "#16a34a")
                    trend = kpi.get("trend", "stable")
                    trend_icon = "↑" if trend == "degrading" else ("↓" if trend == "improving" else "→")
                    trend_color = "#dc2626" if trend == "degrading" else ("#16a34a" if trend == "improving" else "#94a3b8")
                    with col:
                        st.markdown(f"""
                        <div class="mck-kpi-card">
                            <div class="mck-kpi-label">{kpi['kpi'].replace('_',' ').title()}</div>
                            <div class="mck-kpi-value">{kpi['latest_value']} <span style="font-size:14px;">{kpi['unit']}</span></div>
                            <div style="display:flex;justify-content:space-between;margin-top:8px;">
                                <span style="font-size:11px;color:{sev_color};font-weight:600;">{sev.upper()}</span>
                                <span style="font-size:11px;color:{trend_color};font-weight:600;">{trend_icon} {trend.title()}</span>
                            </div>
                            <div style="font-size:10px;color:#94a3b8;margin-top:4px;">Mean: {kpi['mean']} | Z-score: {kpi['z_score']}</div>
                        </div>
                        """, unsafe_allow_html=True)

            # Anomaly Details
            anomalies = ad_result.get("anomalies", [])
            if anomalies:
                st.markdown('<hr style="border:none;border-top:1px solid #e2e8f0;margin:20px 0;">', unsafe_allow_html=True)
                st.markdown('<p class="mck-section-title">Detected Anomalies</p>', unsafe_allow_html=True)
                for a in anomalies:
                    sev = a.get("severity", "normal")
                    sev_color = "#dc2626" if sev == "critical" else "#d97706"
                    css = "mck-alarm-critical" if sev == "critical" else "mck-alarm-major"
                    st.markdown(f"""
                    <div class="{css}">
                        <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:4px;">
                            <div>
                                <span style="font-size:11px;font-weight:700;color:{sev_color};">{sev.upper()}</span>
                                <span style="font-size:12px;color:#475569;margin-left:8px;font-weight:600;">
                                    {a['kpi'].replace('_',' ').title()}
                                </span>
                            </div>
                            <span style="font-size:11px;color:#94a3b8;">Z-score: {a['z_score']}</span>
                        </div>
                        <div style="font-size:12px;color:#64748b;">{a['description']}</div>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.markdown("""
                <div class="mck-card" style="text-align:center;padding:32px;">
                    <div style="font-size:28px;margin-bottom:8px;">✅</div>
                    <div style="font-size:14px;font-weight:700;color:#16a34a;">No Anomalies Detected</div>
                    <div style="font-size:12px;color:#94a3b8;margin-top:4px;">All KPIs within normal ranges</div>
                </div>
                """, unsafe_allow_html=True)

    except requests.exceptions.ConnectionError:
        st.error("❌ API offline. Start the API server first.")
    except Exception as e:
        st.error(f"Error: {e}")

# ══ Tab 4: Config Audit ═══════════════════════════════════════════════════
with tab4:
    st.markdown('<p class="mck-section-title">Configuration Audit</p>', unsafe_allow_html=True)

    ca_c1, ca_c2 = st.columns([2, 5])
    with ca_c1:
        ca_cell = st.selectbox("Select Cell", [f"CELL_{i:03d}" for i in range(1, 11)], key="config_cell")

    try:
        ca_result = requests.get(f"{API_URL}/config/{ca_cell}", timeout=30).json()

        if "error" in ca_result:
            st.error(ca_result["error"])
        else:
            # Config score header
            cscore = ca_result.get("config_score", 0)
            cstatus = ca_result.get("config_status", "")
            cscore_color = "#16a34a" if cscore >= 80 else ("#d97706" if cscore >= 50 else "#dc2626")
            cstatus_label = "OPTIMAL" if cscore >= 80 else ("NEEDS TUNING" if cscore >= 50 else "MISCONFIGURED")

            st.markdown(f"""
            <div class="mck-card-blue" style="margin-bottom:16px;">
                <div style="display:flex;align-items:center;justify-content:space-between;">
                    <div>
                        <div style="font-size:11px;font-weight:700;color:#64a0c8;letter-spacing:1.5px;
                                    text-transform:uppercase;">Configuration Score</div>
                        <div style="font-size:42px;font-weight:800;color:#ffffff;margin-top:4px;">{cscore}</div>
                        <div style="font-size:12px;color:{cscore_color};font-weight:700;margin-top:4px;">{cstatus_label}</div>
                    </div>
                    <div style="text-align:right;">
                        <div style="font-size:11px;color:#94b8d4;">Issues Found</div>
                        <div style="font-size:28px;font-weight:800;color:#ffffff;">{ca_result.get('total_issues',0)}</div>
                        <div style="font-size:11px;color:#ef4444;font-weight:600;">
                            {ca_result.get('critical_issues',0)} Critical · {ca_result.get('warning_issues',0)} Warning
                        </div>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

            # KPI Config Checks
            st.markdown('<p class="mck-section-title">KPI Configuration Checks</p>', unsafe_allow_html=True)
            checks = ca_result.get("kpi_config_checks", [])
            for check in checks:
                status = check.get("status", "ok")
                if status == "critical":
                    icon = "🔴"
                    css = "mck-alarm-critical"
                elif status == "warning":
                    icon = "🟡"
                    css = "mck-alarm-major"
                else:
                    icon = "🟢"
                    css = "mck-alarm-minor"

                st.markdown(f"""
                <div class="{css}">
                    <div style="display:flex;justify-content:space-between;align-items:center;">
                        <div>
                            <span style="font-size:13px;">{icon}</span>
                            <span style="font-size:12px;font-weight:700;color:#0d2b4e;margin-left:6px;">{check['check']}</span>
                            <span style="font-size:11px;color:#94a3b8;margin-left:8px;">{check['parameter']}</span>
                        </div>
                        <span style="font-size:13px;font-weight:700;color:#0d2b4e;">{check['measured_value']}</span>
                    </div>
                    <div style="font-size:11px;color:#64748b;margin-top:4px;">
                        Warn: {check['warn_threshold']} | Crit: {check['crit_threshold']} — {check['recommendation']}
                    </div>
                </div>
                """, unsafe_allow_html=True)

            # Alarm-based Config Issues
            alarm_issues = ca_result.get("alarm_config_issues", [])
            if alarm_issues:
                st.markdown('<hr style="border:none;border-top:1px solid #e2e8f0;margin:20px 0;">', unsafe_allow_html=True)
                st.markdown('<p class="mck-section-title">Alarm-Based Configuration Issues</p>', unsafe_allow_html=True)
                for ai in alarm_issues:
                    sev = ai.get("severity", "major")
                    sev_color = "#dc2626" if sev == "critical" else "#d97706"
                    css = "mck-alarm-critical" if sev == "critical" else "mck-alarm-major"
                    st.markdown(f"""
                    <div class="{css}">
                        <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:6px;">
                            <div>
                                <span style="font-size:11px;font-weight:700;color:{sev_color};">{sev.upper()}</span>
                                <span style="font-size:12px;font-weight:700;color:#0d2b4e;margin-left:8px;">{ai['alarm_type']}</span>
                            </div>
                            <span style="font-size:11px;color:#94a3b8;">{ai.get('alarm_timestamp','')}</span>
                        </div>
                        <div style="font-size:12px;color:#475569;margin-bottom:6px;">
                            <span style="font-weight:600;">Parameter:</span> {ai['parameter']}
                        </div>
                        <div style="font-size:12px;color:#64748b;margin-bottom:6px;">
                            <span style="font-weight:600;">Issue:</span> {ai['issue']}
                        </div>
                        <div style="background:#f0f9ff;border-radius:4px;padding:8px 12px;">
                            <span style="font-size:11px;font-weight:600;color:#0d2b4e;">Recommendation:</span>
                            <span style="font-size:12px;color:#1e40af;"> {ai['recommendation']}</span>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

            # Top Recommendations
            top_recs = ca_result.get("top_recommendations", [])
            if top_recs:
                st.markdown('<hr style="border:none;border-top:1px solid #e2e8f0;margin:20px 0;">', unsafe_allow_html=True)
                st.markdown('<p class="mck-section-title">Top Recommendations</p>', unsafe_allow_html=True)
                for idx, rec in enumerate(top_recs, 1):
                    st.markdown(f"""
                    <div class="mck-rec-card">
                        <div style="display:flex;gap:12px;align-items:flex-start;">
                            <div style="min-width:24px;height:24px;background:#0d2b4e;color:#fff;
                                        border-radius:50%;display:flex;align-items:center;
                                        justify-content:center;font-size:11px;font-weight:700;">{idx}</div>
                            <div class="mck-card-body">{rec}</div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

    except requests.exceptions.ConnectionError:
        st.error("❌ API offline. Start the API server first.")
    except Exception as e:
        st.error(f"Error: {e}")

# ══ Tab 5: Real-Time Analytics & Self-Healing ════════════════════════════════
with tab5:
    st.markdown('<p class="mck-section-title">Real-Time Analytics & Self-Healing</p>', unsafe_allow_html=True)

    rt_c1, rt_c2 = st.columns([2, 5])
    with rt_c1:
        rt_cell = st.selectbox("Select Cell", [f"CELL_{i:03d}" for i in range(1, 11)], key="rt_cell")

    try:
        rt = requests.get(f"{API_URL}/realtime/{rt_cell}", timeout=30).json()

        if "error" in rt:
            st.error(rt["error"])
        else:
            score = rt.get("health_score", 0)
            status = rt.get("health_status", "")
            score_color = "#16a34a" if score >= 80 else ("#d97706" if score >= 50 else "#dc2626")

            # Header card
            st.markdown(f"""
            <div class="mck-card-blue" style="margin-bottom:16px;">
                <div style="display:flex;align-items:center;justify-content:space-between;">
                    <div>
                        <div style="font-size:11px;font-weight:700;color:#64a0c8;letter-spacing:1.5px;
                                    text-transform:uppercase;">Real-Time Cell Health</div>
                        <div style="font-size:42px;font-weight:800;color:#ffffff;margin-top:4px;">{score}</div>
                        <div style="font-size:12px;color:{score_color};font-weight:700;margin-top:4px;">{status.upper()}</div>
                    </div>
                    <div style="text-align:center;">
                        <div style="font-size:11px;color:#94b8d4;">KPIs Monitored</div>
                        <div style="font-size:28px;font-weight:800;color:#ffffff;">{rt.get('kpis_monitored',0)}</div>
                    </div>
                    <div style="text-align:center;">
                        <div style="font-size:11px;color:#94b8d4;">Anomalies</div>
                        <div style="font-size:28px;font-weight:800;color:#ef4444;">{rt.get('anomaly_count',0)}</div>
                    </div>
                    <div style="text-align:center;">
                        <div style="font-size:11px;color:#94b8d4;">Patterns</div>
                        <div style="font-size:28px;font-weight:800;color:#f59e0b;">{rt.get('pattern_count',0)}</div>
                    </div>
                    <div style="text-align:center;">
                        <div style="font-size:11px;color:#94b8d4;">Self-Healing</div>
                        <div style="font-size:28px;font-weight:800;color:#22c55e;">{rt.get('auto_executable_count',0)}</div>
                        <div style="font-size:10px;color:#94b8d4;">auto actions</div>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

            # Category Health
            st.markdown('<p class="mck-section-title">Category Health</p>', unsafe_allow_html=True)
            cats = rt.get("category_health", {})
            cat_cols = st.columns(min(len(cats), 6))
            cat_icons = {"capacity": "📦", "performance": "⚡", "quality": "🎯", "rf": "📡", "mobility": "🚗", "spectral": "🌐"}
            for i, (cat, data) in enumerate(cats.items()):
                cat_color = "#16a34a" if data["score"] >= 80 else ("#d97706" if data["score"] >= 50 else "#dc2626")
                icon = cat_icons.get(cat, "📊")
                with cat_cols[i % len(cat_cols)]:
                    st.markdown(f"""
                    <div class="mck-kpi-card" style="text-align:center;">
                        <div style="font-size:20px;">{icon}</div>
                        <div class="mck-kpi-label" style="margin-top:4px;">{cat.title()}</div>
                        <div style="font-size:28px;font-weight:800;color:{cat_color};">{data['score']}</div>
                        <div style="font-size:11px;color:{cat_color};font-weight:600;">{data['status'].upper()}</div>
                    </div>
                    """, unsafe_allow_html=True)

            # Degradation Patterns
            patterns = rt.get("active_patterns", [])
            if patterns:
                st.markdown('<hr style="border:none;border-top:1px solid #e2e8f0;margin:20px 0;">', unsafe_allow_html=True)
                st.markdown('<p class="mck-section-title">Active Degradation Patterns</p>', unsafe_allow_html=True)

                for p in patterns:
                    sev = p.get("severity", "major")
                    sev_color = "#dc2626" if sev == "critical" else "#d97706"
                    css = "mck-alarm-critical" if sev == "critical" else "mck-alarm-major"

                    st.markdown(f"""
                    <div class="mck-card" style="margin:12px 0;padding:20px 24px;border-left:4px solid {sev_color};">
                        <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:10px;">
                            <div>
                                <span style="font-size:11px;font-weight:700;color:{sev_color};">{sev.upper()}</span>
                                <span style="font-size:14px;font-weight:700;color:#0d2b4e;margin-left:8px;">{p['name']}</span>
                            </div>
                        </div>
                        <div class="mck-card-body" style="margin-bottom:12px;">{p['description']}</div>
                    """, unsafe_allow_html=True)

                    # Affected KPIs
                    affected = p.get("affected_kpis", {})
                    if affected:
                        kpi_html = '<div style="display:flex;gap:8px;flex-wrap:wrap;margin-bottom:12px;">'
                        for kpi_name, kpi_data in affected.items():
                            ks = kpi_data.get("severity", "normal")
                            kc = "#dc2626" if ks == "critical" else ("#d97706" if ks == "warning" else "#16a34a")
                            kpi_html += f'<span style="background:#f8fafc;border:1px solid #e2e8f0;border-radius:4px;padding:4px 8px;font-size:11px;"><span style="color:{kc};font-weight:700;">{ks[0].upper()}</span> {kpi_name}: {kpi_data["latest_value"]}{kpi_data.get("unit","")}</span>'
                        kpi_html += '</div>'
                        st.markdown(kpi_html, unsafe_allow_html=True)

                    # Self-healing actions
                    st.markdown('<div style="font-size:10px;font-weight:700;color:#0d2b4e;text-transform:uppercase;letter-spacing:1px;margin-bottom:8px;">Self-Healing Actions</div>', unsafe_allow_html=True)
                    for idx, action in enumerate(p.get("self_healing_actions", []), 1):
                        auto = action.get("auto_executable", False)
                        auto_badge = '<span style="background:#d1fae5;color:#065f46;font-size:10px;font-weight:700;padding:2px 6px;border-radius:3px;">AUTO</span>' if auto else '<span style="background:#fef3c7;color:#92400e;font-size:10px;font-weight:700;padding:2px 6px;border-radius:3px;">MANUAL</span>'
                        st.markdown(f"""
                        <div class="mck-rec-card">
                            <div style="display:flex;gap:10px;align-items:flex-start;">
                                <div style="min-width:24px;height:24px;background:#0d2b4e;color:#fff;
                                            border-radius:50%;display:flex;align-items:center;
                                            justify-content:center;font-size:11px;font-weight:700;">{idx}</div>
                                <div style="flex:1;">
                                    <div style="display:flex;align-items:center;gap:8px;margin-bottom:4px;">
                                        {auto_badge}
                                        <span style="font-size:12px;font-weight:700;color:#0d2b4e;">{action['action']}</span>
                                    </div>
                                    <div class="mck-card-body">{action['description']}</div>
                                    <div style="font-size:11px;color:#94a3b8;margin-top:4px;">Parameter: {action['parameter']}</div>
                                </div>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)

                    st.markdown('</div>', unsafe_allow_html=True)
            else:
                st.markdown('<hr style="border:none;border-top:1px solid #e2e8f0;margin:20px 0;">', unsafe_allow_html=True)
                st.markdown("""
                <div class="mck-card" style="text-align:center;padding:32px;">
                    <div style="font-size:28px;margin-bottom:8px;">✅</div>
                    <div style="font-size:14px;font-weight:700;color:#16a34a;">No Degradation Patterns Detected</div>
                    <div style="font-size:12px;color:#94a3b8;margin-top:4px;">All KPI correlation chains are within normal ranges</div>
                </div>
                """, unsafe_allow_html=True)

            # Anomaly Summary Table
            anomalies = rt.get("anomalies", [])
            if anomalies:
                st.markdown('<hr style="border:none;border-top:1px solid #e2e8f0;margin:20px 0;">', unsafe_allow_html=True)
                st.markdown('<p class="mck-section-title">All Detected Anomalies</p>', unsafe_allow_html=True)
                anom_df = pd.DataFrame([{
                    "KPI": a.get("kpi", "").replace("_", " ").title(),
                    "Value": f"{a.get('latest_value','')}{a.get('unit','')}",
                    "Severity": a.get("severity", "").upper(),
                    "Z-Score": a.get("z_score", 0),
                    "Trend": a.get("trend", "").title(),
                    "Category": a.get("category", "").title(),
                } for a in anomalies])
                st.dataframe(anom_df, width="stretch", hide_index=True)

    except requests.exceptions.ConnectionError:
        st.error("❌ API offline. Start the API server first.")
    except Exception as e:
        st.error(f"Error: {e}")

# ══ Step 5a + 5b: History Tab ════════════════════════════════════════════════
with tab6:
    st.markdown('<p class="mck-section-title">Analysis History</p>', unsafe_allow_html=True)

    if not st.session_state.history:
        st.markdown("""
        <div class="empty-state">
            <div style="font-size:40px;margin-bottom:12px;">📜</div>
            <div style="font-size:15px;font-weight:700;color:#0d2b4e;margin-bottom:6px;">No History Yet</div>
            <div style="font-size:13px;color:#94a3b8;">Run some analyses to see history here</div>
        </div>
        """, unsafe_allow_html=True)
    else:
        history = st.session_state.history

        # Step 5a: Summary metrics
        issue_counts = {}
        for h in history:
            issue_counts[h["issue_type"]] = issue_counts.get(h["issue_type"], 0) + 1

        m1, m2, m3, m4 = st.columns(4)
        with m1: st.metric("Total Analyses", len(history))
        with m2: st.metric("Avg Confidence", f"{sum(h['confidence'] for h in history)/len(history)*100:.0f}%")
        with m3: st.metric("Most Common", max(issue_counts, key=issue_counts.get).replace("_"," ").title())
        with m4: st.metric("Unique Cells", len(set(h["cell_id"] for h in history)))

        # Issue distribution
        if len(issue_counts) > 1:
            st.markdown('<hr style="border:none;border-top:1px solid #e2e8f0;margin:20px 0;">', unsafe_allow_html=True)
            st.markdown('<p class="mck-section-title">Issue Distribution</p>', unsafe_allow_html=True)
            dist_cols = st.columns(min(len(issue_counts), 5))
            for i, (iss, cnt) in enumerate(sorted(issue_counts.items(), key=lambda x: -x[1])):
                bclass_i = badge_class(iss)
                pct = cnt / len(history) * 100
                with dist_cols[i % len(dist_cols)]:
                    st.markdown(f"""
                    <div class="mck-kpi-card" style="text-align:center;">
                        <div class="mck-kpi-value">{cnt}</div>
                        <div style="font-size:11px;color:#94a3b8;margin:4px 0;">{pct:.0f}% of total</div>
                        <span class="badge {bclass_i}">{iss.replace("_"," ").upper()}</span>
                    </div>
                    """, unsafe_allow_html=True)

        # Step 5b: Table
        st.markdown('<hr style="border:none;border-top:1px solid #e2e8f0;margin:20px 0;">', unsafe_allow_html=True)
        st.markdown('<p class="mck-section-title">All Analyses</p>', unsafe_allow_html=True)

        hist_df = pd.DataFrame([{
            "Time":       h.get("timestamp", ""),
            "Cell":       h.get("cell_id", ""),
            "Issue Type": h.get("issue_type", "").replace("_", " ").title(),
            "Confidence": f"{h.get('confidence', 0)*100:.0f}%",
            "Query":      h.get("query", "")[:50] + "...",
        } for h in reversed(history)])

        st.dataframe(hist_df, width="stretch", hide_index=True)

        # Detailed view
        st.markdown('<hr style="border:none;border-top:1px solid #e2e8f0;margin:20px 0;">', unsafe_allow_html=True)
        st.markdown('<p class="mck-section-title">Detailed View</p>', unsafe_allow_html=True)

        for i, h in enumerate(reversed(history)):
            issue_h  = h.get("issue_type", "unknown")
            conf_h   = h.get("confidence", 0)
            cell_h   = h.get("cell_id", "")
            ts_h     = h.get("timestamp", "")
            query_h  = h.get("query", "")
            analysis_h = h.get("analysis", "")
            recs_h   = h.get("recommendation", "").replace("**", "")
            bclass_h = badge_class(issue_h)
            bar_col  = confidence_color(conf_h)

            # Full card — no expander, no arrows
            st.markdown(f"""
            <div class="mck-card" style="margin:12px 0;padding:20px 24px;">
                <div style="display:flex;align-items:center;justify-content:space-between;
                            padding-bottom:12px;margin-bottom:14px;border-bottom:1px solid #e2e8f0;">
                    <div style="display:flex;align-items:center;gap:10px;">
                        <span class="badge {bclass_h}">{issue_h.replace("_"," ").upper()}</span>
                        <span style="font-size:13px;font-weight:700;color:#0d2b4e;">{cell_h}</span>
                        <span style="font-size:11px;color:#94a3b8;">{ts_h}</span>
                    </div>
                    <span style="font-size:18px;font-weight:800;color:{bar_col};">{conf_h*100:.0f}%</span>
                </div>
            """, unsafe_allow_html=True)

            # Query
            st.markdown(f"""
                <div style="background:#f8fafc;border-radius:6px;padding:10px 14px;margin-bottom:14px;">
                    <div style="font-size:10px;font-weight:700;color:#94a3b8;text-transform:uppercase;
                                letter-spacing:1px;margin-bottom:4px;">Query</div>
                    <div style="font-size:13px;color:#1e293b;">{query_h}</div>
                </div>
            """, unsafe_allow_html=True)

            # Root Cause
            st.markdown(f"""
                <div style="border-left:4px solid #0d2b4e;padding:12px 16px;margin-bottom:14px;
                            background:#ffffff;border-radius:0 6px 6px 0;">
                    <div style="font-size:10px;font-weight:700;color:#0d2b4e;text-transform:uppercase;
                                letter-spacing:1px;margin-bottom:6px;">Root Cause Analysis</div>
                    <div class="mck-card-body">{analysis_h}</div>
                </div>
            """, unsafe_allow_html=True)

            # Recommendations — numbered
            st.markdown("""
                <div style="font-size:10px;font-weight:700;color:#0d2b4e;text-transform:uppercase;
                            letter-spacing:1px;margin-bottom:8px;">Recommendations</div>
            """, unsafe_allow_html=True)

            rec_lines = [l.strip() for l in recs_h.split("\n") if l.strip()]
            rec_num = 0
            rec_html = ""
            for line in rec_lines:
                if line and (line[0].isdigit() or line.startswith("-") or line.startswith("*")):
                    rec_num += 1
                    clean = line.lstrip("0123456789.-* ").strip()
                    if ":" in clean:
                        title_part, desc_part = clean.split(":", 1)
                        rec_html += f"""
                        <div class="mck-rec-card">
                            <div style="display:flex;gap:12px;align-items:flex-start;">
                                <div style="min-width:24px;height:24px;background:#0d2b4e;color:#fff;
                                            border-radius:50%;display:flex;align-items:center;
                                            justify-content:center;font-size:11px;font-weight:700;">{rec_num}</div>
                                <div>
                                    <div style="font-size:13px;font-weight:700;color:#0d2b4e;margin-bottom:3px;">{title_part.strip()}</div>
                                    <div class="mck-card-body">{desc_part.strip()}</div>
                                </div>
                            </div>
                        </div>"""
                    else:
                        rec_html += f"""
                        <div class="mck-rec-card">
                            <div style="display:flex;gap:12px;align-items:flex-start;">
                                <div style="min-width:24px;height:24px;background:#0d2b4e;color:#fff;
                                            border-radius:50%;display:flex;align-items:center;
                                            justify-content:center;font-size:11px;font-weight:700;">{rec_num}</div>
                                <div class="mck-card-body">{clean}</div>
                            </div>
                        </div>"""
                elif line and rec_num > 0:
                    rec_html += f'<div style="padding:2px 0 2px 36px;"><div class="mck-card-body">{line}</div></div>'

            st.markdown(rec_html, unsafe_allow_html=True)

            # Close card
            st.markdown('</div>', unsafe_allow_html=True)
