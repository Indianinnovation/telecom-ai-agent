from typing import TypedDict, Annotated
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langchain_core.messages import HumanMessage, AIMessage
from langchain_aws import ChatBedrock
from langchain_openai import ChatOpenAI
from app.tools.kpi_tool import get_kpis
from app.tools.alarm_tool import get_alarms
from app.tools.log_tool import get_logs
from dotenv import load_dotenv
import json
import os

# Load .env file
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), "../../.env"))

# ── LLM Setup ──────────────────────────────────────────────────────────────
def get_llm():
    """Use OpenAI if key exists, else AWS Bedrock."""
    if os.getenv("OPENAI_API_KEY"):
        return ChatOpenAI(model="gpt-4o-mini", temperature=0)
    return ChatBedrock(
        model_id="anthropic.claude-3-haiku-20240307-v1:0",
        region_name=os.getenv("AWS_DEFAULT_REGION", "us-east-1")
    )

llm = get_llm()

# ── State ───────────────────────────────────────────────────────────────────
class AgentState(TypedDict):
    query:          str
    cell_id:        str
    ne_id:          str
    issue_type:     str
    kpi_data:       dict
    alarm_data:     dict
    log_data:       dict
    analysis:       str
    recommendation: str
    confidence:     float
    retry_count:    int
    messages:       Annotated[list, add_messages]

# ── Node 1: Classify Issue (LLM + Telemetry + Alarms) ──────────────────────
def classify_issue(state: AgentState) -> AgentState:
    # Retrieve telemetry first so LLM can use real data
    kpi_data   = get_kpis(state["cell_id"])
    alarm_data = get_alarms(state["ne_id"])
    log_data   = get_logs(state["ne_id"])

    prompt = f"""You are a senior telecom RAN engineer. Analyze the retrieved telemetry, alarms, and logs below.
Classify the issue into EXACTLY ONE of these categories based on these rules:

- congestion: PRB Utilization > 80% OR RRC Connected Users > 250 OR active CONGESTION/HIGH_PRB alarm
- interference: SINR < 3 dB AND BLER > 10%, OR active INTERFERENCE/LOW_SINR alarm
- bler_issue: BLER > 10% OR active HIGH_BLER/HIGH_RETRANSMISSION alarm (when not interference)
- link_failure: Active S1/X2/BACKHAUL/LINK_FAILURE alarm OR "link failure" / "out of service" in logs
- hardware_fault: Active POWER_DEGRADATION/TX_POWER/ANTENNA/VSWR alarm
- coverage_issue: Low throughput (< 20 Mbps) despite low PRB utilization (< 40%) and low SINR (< 5 dB)
- healthy: All KPIs within nominal ranges AND no active alarms

User Query: {state['query']}
Cell ID: {state['cell_id']}

KPI Data:
{json.dumps(kpi_data, indent=2)}

Active Alarms:
{json.dumps(alarm_data, indent=2)}

Recent Logs:
{json.dumps(log_data, indent=2)}

IMPORTANT:
- Do NOT return "unknown". Always pick the best matching category from the rules above.
- If multiple issues exist, pick the most severe one (link_failure > hardware_fault > interference > congestion > bler_issue > coverage_issue > healthy).
- Reply with ONLY the single-word category name, nothing else."""

    response = llm.invoke([HumanMessage(content=prompt)])
    issue_type = response.content.strip().lower().replace(" ", "_")

    valid = ["congestion", "bler_issue", "interference", "link_failure",
             "hardware_fault", "coverage_issue", "healthy"]
    if issue_type not in valid:
        issue_type = "congestion"  # safe fallback, never unknown

    return {**state,
            "issue_type": issue_type,
            "kpi_data":   kpi_data,
            "alarm_data": alarm_data,
            "log_data":   log_data,
            "messages":   [AIMessage(content=f"Classified as: {issue_type}")]}

# ── Node 2: Retrieve Data (pass-through, already fetched in classify) ───────
def retrieve_data(state: AgentState) -> AgentState:
    if not state.get("kpi_data") or "error" in state.get("kpi_data", {}):
        kpi_data   = get_kpis(state["cell_id"])
        alarm_data = get_alarms(state["ne_id"])
        log_data   = get_logs(state["ne_id"])
        return {**state,
                "kpi_data":   kpi_data,
                "alarm_data": alarm_data,
                "log_data":   log_data,
                "messages":   [AIMessage(content="Data retrieved from KPI, alarms, and logs.")]}
    return {**state,
            "messages": [AIMessage(content="Data already available from classification step.")]}

# ── Node 3: Analyze Issue ───────────────────────────────────────────────────
def analyze_issue(state: AgentState) -> AgentState:
    prompt = f"""You are a telecom RCA (Root Cause Analysis) expert.

Issue Type: {state['issue_type']}
Query: {state['query']}

KPI Data:
{json.dumps(state['kpi_data'], indent=2)}

Active Alarms:
{json.dumps(state['alarm_data'], indent=2)}

Recent Logs:
{json.dumps(state['log_data'], indent=2)}

Provide a concise root cause analysis in 3-4 sentences.
Focus on the most likely root cause based on the data."""

    response = llm.invoke([HumanMessage(content=prompt)])
    return {**state, "analysis": response.content.strip(),
            "messages": [AIMessage(content="Analysis complete.")]}

# ── Node 4: Recommend Action ────────────────────────────────────────────────
def recommend_action(state: AgentState) -> AgentState:
    prompt = f"""You are a telecom network optimization expert.

Issue Type: {state['issue_type']}
Analysis: {state['analysis']}

KPI Summary:
- PRB Utilization: {state['kpi_data'].get('avg_prb_utilization', 'N/A')}%
- Throughput: {state['kpi_data'].get('avg_throughput_mbps', 'N/A')} Mbps
- BLER: {state['kpi_data'].get('avg_bler_pct', 'N/A')}%
- SINR: {state['kpi_data'].get('avg_sinr_db', 'N/A')} dB

Provide 3 specific, actionable recommendations to resolve this issue.
Format as a numbered list."""

    response = llm.invoke([HumanMessage(content=prompt)])

    # Estimate confidence based on data quality
    has_alarms = state["alarm_data"].get("count", 0) > 0
    has_errors = state["log_data"].get("error_count", 0) > 0
    confidence = 0.60
    if has_alarms: confidence += 0.15
    if has_errors: confidence += 0.15
    if state["issue_type"] != "unknown": confidence += 0.10

    return {**state,
            "recommendation": response.content.strip(),
            "confidence": round(min(confidence, 0.99), 2),
            "messages": [AIMessage(content="Recommendations generated.")]}

# ── Node 5: Validate Output ─────────────────────────────────────────────────
def validate_output(state: AgentState) -> AgentState:
    """Validate output quality, retry if needed."""
    retry_count = state.get("retry_count", 0)

    if not state["analysis"] or len(state["analysis"]) < 20:
        if retry_count < 2:
            return {**state, "retry_count": retry_count + 1,
                    "messages": [AIMessage(content=f"Retrying... attempt {retry_count + 1}")]}

    return {**state, "messages": [AIMessage(content="Validation passed. Output ready.")]}

# ── Retry Router ────────────────────────────────────────────────────────────
def should_retry(state: AgentState) -> str:
    if state.get("retry_count", 0) > 0 and state.get("retry_count", 0) <= 2:
        if not state["analysis"] or len(state["analysis"]) < 20:
            return "analyze_issue"
    return END

# ── Build Graph ─────────────────────────────────────────────────────────────
def build_graph():
    graph = StateGraph(AgentState)

    graph.add_node("classify_issue",   classify_issue)
    graph.add_node("retrieve_data",    retrieve_data)
    graph.add_node("analyze_issue",    analyze_issue)
    graph.add_node("recommend_action", recommend_action)
    graph.add_node("validate_output",  validate_output)

    graph.add_edge(START,              "classify_issue")
    graph.add_edge("classify_issue",   "retrieve_data")
    graph.add_edge("retrieve_data",    "analyze_issue")
    graph.add_edge("analyze_issue",    "recommend_action")
    graph.add_edge("recommend_action", "validate_output")
    graph.add_conditional_edges("validate_output", should_retry)

    return graph.compile()

agent = build_graph()
