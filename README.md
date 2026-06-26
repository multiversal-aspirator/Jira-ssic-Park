# 🦖 Jirassic Park — AI Project Manager Command Center

> *"Life, uh... finds a way" — and so do your project blockers.*

An autonomous AI coordination layer for engineering teams. Five specialist LLM agents hunt your Jira, GitHub, and Microsoft Teams data to generate real-time project health reports, surface risks, map dependency chains, and produce stakeholder-ready summaries — all from a single click.

---

## 🎯 What It Does

- **Analyzes your active sprint** — completion %, velocity, blocked issues, story point burn
- **Detects risks** — blockers, stale PRs, failing checks, team communication signals
- **Maps dependencies** — issue links, PR chains, critical path, conflict detection
- **Forecasts delivery** — predicted completion date, confidence score, trend direction
- **Generates executive reports** — highlights, concerns, next steps in plain English
- **Semantic search & RAG** — ask natural language questions about your project history
- **Live event feed** — ingests GitHub/Jira/Teams webhooks into a vector store in real time

---

## 🏗️ Architecture

```
Browser (React + Vite)
        │  REST
        ▼
FastAPI  (port 8000)
  ├── POST /api/project/analyze      → LangGraph Orchestrator
  ├── POST /api/intelligence/sync    → Batch vector store sync
  ├── POST /api/intelligence/ask     → RAG Q&A (ChromaDB + GPT-4o)
  ├── GET  /api/intelligence/search  → Semantic search
  ├── GET  /api/team/overview        → Team workload analysis
  └── POST /api/webhooks/{github,jira,teams}  → Real-time ingestion

LangGraph Orchestrator (sequential DAG)
  load_project_context
        ↓
  analyze_sprint   (SprintAgent  — Steggy 🦕)
        ↓
  detect_risks     (RiskAgent    — Rexford 🦖)
        ↓
  track_dependencies (DependencyAgent — Velocity 🦅)
        ↓
  forecast_delivery  (ForecastingAgent — Skyview 🦋)
        ↓
  generate_report  (ReportingAgent  — Alto 🦒)
        ↓ (conditional — fires on HIGH/CRITICAL risk or OFF_TRACK sprint)
  [escalation_node]
        ↓
  merge_results  → ProjectHealthReport (score 0–100)

Vector Store (ChromaDB — 6 collections)
  github_commits │ github_prs │ jira_tickets
  teams_messages │ meeting_notes │ generated_reports
```

---

## 🤖 The Agent Pack

| Agent | Nickname | Species | Data Sources | Output |
|-------|----------|---------|-------------|--------|
| Sprint Agent | Steggy | 🦕 Stego | Jira sprint (JQL) | `SprintAnalysis` — velocity, completion %, status |
| Risk Agent | Rexford | 🦖 T-Rex | Jira + GitHub + Teams | `RiskAnalysis` — severity-ranked risks with evidence |
| Dependency Agent | Velocity | 🦅 Raptor | Jira issue links + GitHub PRs | `DependencyAnalysis` — blocking map + critical path |
| Forecasting Agent | Skyview | 🦋 Pterodactyl | Jira + Sprint output | `DeliveryForecast` — ETA + confidence score |
| Reporting Agent | Alto | 🦒 Brachiosaurus | All agent outputs | `StakeholderReport` — exec summary, highlights, next steps |

Each agent follows the same pattern:
1. Fetch real data from the configured integration
2. Pass to GPT-4o with a structured JSON prompt
3. Validate output with Pydantic models
4. **Fall back to deterministic demo data** if LLM or API call fails — the pipeline never crashes

---

## 🛠️ Tech Stack

| Layer | Technology | Version |
|-------|-----------|---------|
| Orchestration | LangGraph `StateGraph` | 0.2.76 |
| LLM | OpenAI GPT-4o via LangChain | langchain 0.3.0 |
| Backend | FastAPI + Uvicorn | 0.115.0 |
| Vector Store | ChromaDB (persistent, ONNX embeddings) | 0.5.0 |
| Frontend | React 18 + Vite | React 18.3, Vite 7 |
| HTTP Client | httpx (async) | 0.27.0 |
| Integrations | Jira REST API v3, GitHub REST API v3, MS Teams Graph API | — |
| Observability | LangSmith tracing (`@traceable`) | ≥ 0.1.0 |
| MCP | Model Context Protocol server exposing all tools | ≥ 1.0.0 |
| Scheduling | APScheduler (background sync) | 3.10.4 |

---

## 📁 Project Structure

```
Jira-sick-park/
├── frontend/
│   ├── src/
│   │   ├── App.jsx                 # Main app — tabs, form, agent animation
│   │   ├── index.css               # All styles (dark jungle theme)
│   │   └── components/
│   │       ├── AgentGrid.jsx       # 5 animated agent cards with progress bars
│   │       ├── AgentCard.jsx       # Individual agent — status, thought bubble
│   │       ├── HealthScore.jsx     # Circular health gauge + evidence chips
│   │       ├── SprintCard.jsx      # Donut chart — done/active/blocked/todo
│   │       ├── RiskCard.jsx        # Severity-ranked risk rows
│   │       ├── DependencyCard.jsx  # Blocking map + critical path
│   │       ├── ForecastCard.jsx    # Confidence gauge + ETA + trend
│   │       ├── ReportCard.jsx      # Exec summary in 3 columns
│   │       ├── TeamCard.jsx        # Per-member workload bars
│   │       ├── SearchPanel.jsx     # Ask AI / Semantic Search
│   │       ├── EventFeed.jsx       # Live webhook event log
│   │       ├── ProjectManager.jsx  # Saved projects (localStorage)
│   │       ├── Visuals.jsx         # CircularGauge, Donut, Kpi, Chip, MiniBar
│   │       └── DinoIcon.jsx        # SVG dino icons per agent species
│   ├── package.json
│   └── vite.config.js              # Vite dev server proxies /api → :8000
│
├── backend/
│   ├── app/
│   │   ├── main.py                 # FastAPI app init + CORS + router mounts
│   │   ├── api/
│   │   │   ├── project_routes.py   # POST /analyze, GET /health-report
│   │   │   ├── intelligence_routes.py  # sync, ask, search, events
│   │   │   ├── team_routes.py      # team overview + per-member summary
│   │   │   └── webhook_routes.py   # GitHub / Jira / Teams webhooks
│   │   ├── agents/
│   │   │   ├── sprint_agent.py
│   │   │   ├── risk_agent.py
│   │   │   ├── dependency_agent.py
│   │   │   ├── forecasting_agent.py
│   │   │   └── reporting_agent.py
│   │   ├── orchestrator/
│   │   │   └── workflow.py         # LangGraph DAG + health score formula
│   │   ├── services/
│   │   │   ├── jira_service.py     # JQL search, issue normalization
│   │   │   ├── github_service.py   # PRs, commits, issues
│   │   │   ├── teams_service.py    # MS Graph API + local .txt fallback
│   │   │   ├── vector_store.py     # ChromaDB wrapper (6 collections)
│   │   │   ├── llm_service.py      # ChatOpenAI factory
│   │   │   ├── demo_data_service.py  # JSON/MD demo data loader
│   │   │   ├── event_processor.py  # In-memory event queue (deque)
│   │   │   └── notes_service.py    # Teams channel / local .md notes
│   │   ├── models/
│   │   │   └── project_models.py   # Pydantic schemas for all agent I/O
│   │   ├── core/
│   │   │   └── config.py           # Pydantic settings from .env
│   │   ├── mcp_services_server.py  # MCP tool server
│   │   └── utils/
│   │       └── logger.py           # Structured JSON logging
│   ├── requirements.txt
│   └── data/                       # Demo data (JSON + MD files)
│       ├── jira_issues.json
│       ├── github_prs.json
│       ├── teams_messages.json
│       └── meeting_notes.md
│
├── Messages/                       # Local Teams transcript fallback (.txt files)
├── .env.example
└── README.md
```

---

## ⚡ Setup

### Prerequisites

- Python **3.12+**
- Node.js **20+**
- API keys (all optional — app runs in demo mode without them):
  - `OPENAI_API_KEY` — required for real LLM analysis
  - `JIRA_URL` + `JIRA_EMAIL` + `JIRA_API_TOKEN` — for live Jira data
  - `GITHUB_TOKEN` — for PR/commit data
  - `TEAMS_ACCESS_TOKEN` — for MS Teams messages (falls back to `Messages/` folder)
  - `LANGCHAIN_API_KEY` — optional LangSmith tracing

### 1. Clone & Configure

```bash
git clone https://github.com/aman-sharma_gep1/Jira-sick-park.git
cd Jira-sick-park
cp .env.example .env
# Fill in .env with your keys — leave blank to run in demo mode
```

### 2. Backend

```bash
cd backend
python -m venv venv

# Windows
venv\Scripts\activate

# macOS / Linux
# source venv/bin/activate

pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

API available at **`http://localhost:8000`** · Swagger UI at **`/docs`**

### 3. Frontend

```bash
cd frontend
npm install
npm run dev
```

Dashboard available at **`http://localhost:5173`**
All `/api/*` calls are proxied to `localhost:8000` by Vite.

### 4. Docker (Alternative)

```bash
# From repo root
docker-compose up --build
```

---

## 🔌 API Reference

### `POST /api/project/analyze`
Run the full 5-agent LangGraph workflow.

```json
{
  "project_key": "SCRUM",
  "sprint_id": "42",
  "github_repo": "org/repo",
  "teams_channel": "channel-id",
  "include_forecasting": true
}
```

Returns `ProjectHealthReport`:
```json
{
  "health_score": 72,
  "sprint_analysis": { "completion_percentage": 68, "velocity": 34, "status": "at_risk" },
  "risk_analysis": { "overall_risk_level": "high", "risks": [...] },
  "dependency_analysis": { "dependencies": [...], "critical_path": [...] },
  "delivery_forecast": { "predicted_completion_date": "2026-06-30", "confidence_score": 0.71 },
  "stakeholder_report": { "executive_summary": "...", "highlights": [...], "concerns": [...] },
  "evidence_summary": ["68% sprint completion", "2 blocking dependencies"],
  "agent_trace": ["load_project_context", "analyze_sprint", ...]
}
```

### `POST /api/intelligence/sync`
Batch-ingest Jira issues, GitHub PRs, and Teams messages into ChromaDB.

```
POST /api/intelligence/sync?project_key=SCRUM&github_repo=org/repo&teams_channel=channel-id
```

### `POST /api/intelligence/ask`
RAG Q&A — asks GPT-4o a question grounded in your project's vector store.

```json
{ "question": "What are the main blockers this sprint?", "project_key": "SCRUM" }
```

### `GET /api/intelligence/search`
Semantic search across all 6 ChromaDB collections.

```
GET /api/intelligence/search?query=authentication+bug&limit=10
```

### `GET /api/team/overview`
Returns per-member workload, open PRs, blocked items, and rebalancing recommendations.

### Webhooks (real-time ingestion)

| Endpoint | Source | Events handled |
|----------|--------|----------------|
| `POST /api/webhooks/github` | GitHub | `push`, `pull_request`, `issues` |
| `POST /api/webhooks/jira` | Jira | `issue_created`, `issue_updated`, `issue_deleted` |
| `POST /api/webhooks/teams` | MS Teams | channel message notifications |

All webhook endpoints always return `200 Accepted` — processing errors are logged but never surfaced to the caller to prevent retry storms.

---

## 🎨 Frontend Features

- **Dark jungle theme** with dino-branded agents (each agent = a dinosaur species)
- **Animated agent cards** — progress bars and thought bubbles during analysis
- **8-tab dashboard**: Overview · Agents · Sprint · Risks · Dependencies · Team · Reports · Search
- **Project persistence** — project configs saved to `localStorage`
- **One-click links** — direct jump to Jira board, GitHub repo, and PR list from the header
- **Live event feed** — real-time webhook ingestion status

---

## 🧠 Design Decisions

| Decision | Rationale |
|----------|-----------|
| **LangGraph over CrewAI** | Explicit DAG control, deterministic ordering, conditional escalation node |
| **Sequential workflow** | Agents share state — Risk Agent enriches its analysis using Sprint Agent output |
| **Pydantic-enforced JSON** | Every agent returns structured, validated output — no hallucinated fields |
| **Graceful degradation** | Every agent has a `try → LLM → deterministic fallback` pattern. The pipeline never crashes |
| **Evidence-based health score** | Score derived from concrete metrics (completion %, risk counts, confidence). Not LLM opinion |
| **Batch ChromaDB upserts** | All ingest methods batch documents into a single `upsert()` call — 58 issues → 1 call |
| **ChromaDB ONNX silenced** | The `onnx_mini_lm_l6_v2` logger is set to `WARNING` to suppress per-call noise |
| **Teams local fallback** | `TeamsService` reads from `Messages/*.txt` when no access token is configured |
| **MCP server** | All tools exposed via Model Context Protocol for external agent interoperability |

---

## ⚠️ Known Limitations

- **Jira pagination capped at 100 issues** — projects with > 100 open issues will have incomplete sprint analysis (a paginator loop is a future TODO)
- **LangGraph agents run sequentially** — the architecture diagram shows the intended dependency ordering; true async parallelism is not implemented in this LangGraph version
- **No HMAC signature verification on webhooks** — GitHub/Jira webhooks are accepted without secret verification (TODO for production hardening)
- **`get_vector_store()` singleton is not thread-safe** — concurrent requests could create two ChromaDB clients; safe under single-worker Uvicorn but needs an `asyncio.Lock` for multi-worker deployments
- **Prompt injection not mitigated** in `/api/intelligence/ask` — user question is interpolated directly into the LLM prompt
- **Meeting notes** ingestion is file-based (`.md` / `.txt` in `Messages/`); no live transcription pipeline

---

## 🔑 Environment Variables

```env
# ── LLM ──────────────────────────────────────────
OPENAI_API_KEY=sk-...
LLM_MODEL=gpt-4o
LLM_TEMPERATURE=0.2

# ── Jira ─────────────────────────────────────────
JIRA_URL=https://your-domain.atlassian.net
JIRA_EMAIL=you@example.com
JIRA_API_TOKEN=your-jira-api-token

# ── GitHub ───────────────────────────────────────
GITHUB_TOKEN=ghp_...

# ── Microsoft Teams (Graph API) ──────────────────
TEAMS_ACCESS_TOKEN=your-ms-graph-token
TEAMS_TEAM_ID=your-team-id

# ── LangSmith Observability (optional) ───────────
LANGCHAIN_TRACING_V2=true
LANGSMITH_ENDPOINT=https://api.smith.langchain.com
LANGCHAIN_API_KEY=ls__...
LANGCHAIN_PROJECT=jirassic-park
```

> **Demo mode**: Leave all keys blank and the system will run entirely on local JSON/MD demo data. No API calls are made.

---

## 🦕 Agent Name → Species Map

| Agent | Name | Species |
|-------|------|---------|
| Sprint | Steggy | Stegosaurus |
| Risk | Rexford | T-Rex |
| Dependency | Velocity | Velociraptor |
| Forecasting | Skyview | Pterodactyl |
| Reporting | Alto | Brachiosaurus |

---

*Built for the GEP AI Hackathon 2026 — Problem Statement 5: Autonomous AI Coordination for Engineering Teams*
