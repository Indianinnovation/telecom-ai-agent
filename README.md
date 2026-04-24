# 📡 Telecom Network Intelligence — AI Agent Platform

AI-powered Root Cause Analysis for telecom networks using **LangGraph + OpenAI + FastAPI + Streamlit**.

## 🎯 Features

- **LangGraph Agent Workflow** — 5-node pipeline: Classify → Retrieve → Analyze → Recommend → Validate
- **LLM-based Classification** — Uses real KPI data + alarms + logs to classify issues (never returns "unknown")
- **6 Issue Categories** — Congestion, Interference, BLER Issue, Link Failure, Hardware Fault, Coverage Issue, Healthy
- **Spectrum Efficiency Optimization** — PRB analysis, frequency planning, capacity health checks
- **Network-Wide Scan** — Batch analysis across multiple cells
- **McKinsey-style UI** — Professional Streamlit dashboard with KPI monitoring

## 🏗️ Architecture

```
User → Streamlit UI → FastAPI → LangGraph Agent → OpenAI → Response
                                      ↓
                              Tools: KPI (CSV) + Alarms (JSON) + Logs (TXT)
```
<img width="1505" height="821" alt="image" src="https://github.com/user-attachments/assets/ed096a75-855f-4099-ad68-9cb4c80762ec" />

## 📁 Project Structure

```
telecom_agent/
├── app/
│   ├── api/routes.py          # FastAPI endpoints
│   ├── graph/agent.py         # LangGraph 5-node workflow
│   ├── tools/
│   │   ├── kpi_tool.py        # KPI reader (CSV)
│   │   ├── alarm_tool.py      # Alarm reader (JSON)
│   │   └── log_tool.py        # Log reader (TXT)
│   ├── models/schemas.py      # Pydantic models
│   └── main.py                # FastAPI entry point
├── data/
│   ├── kpi_data.csv           # Sample KPI data (480 rows)
│   ├── alarms.json            # Sample alarms (8 alarms)
│   └── logs.txt               # Sample system logs
├── ui.py                      # Streamlit McKinsey-style UI
├── requirements.txt
├── .gitignore
└── README.md
```

## 🚀 Quick Start

### 1. Clone & Install
```bash
git clone https://github.com/Indianinnovation/telecom-ai-agent.git
cd telecom-ai-agent
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Add API Key
```bash
echo "OPENAI_API_KEY=your_key_here" > .env
```

### 3. Start API Server
```bash
uvicorn app.main:app --reload --port 8000
```

### 4. Start UI (new terminal)
```bash
streamlit run ui.py
```

### 5. Open Browser
```
http://localhost:8502
```

## 🧪 Test Scenarios

| Scenario | Cell | Expected Issue |
|---|---|---|
| Throughput Drop | CELL_001 | Congestion |
| High BLER | CELL_002 | Interference / BLER Issue |
| Cell Congestion | CELL_003 | Congestion |
| Low SINR | CELL_005 | Interference |
| Link Failure | CELL_007 | Link Failure |

## 📊 API Endpoints

```bash
# Health check
curl http://localhost:8000/health

# Analyze
curl -X POST http://localhost:8000/analyze \
  -H "Content-Type: application/json" \
  -d '{"query": "Throughput dropped", "cell_id": "CELL_001", "ne_id": "CELL_001"}'
```

## 🛠️ Tech Stack

- **FastAPI** — REST API
- **LangGraph** — Agent orchestration
- **OpenAI GPT-4o-mini** — LLM
- **Streamlit** — UI Dashboard
- **Pandas** — Data processing

## 📜 License

MIT
