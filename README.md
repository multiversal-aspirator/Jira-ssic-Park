<<<<<<< HEAD
# AI Project Manager for Engineering Teams

An autonomous AI coordination layer that analyzes project artifacts, identifies risks, tracks delivery progress, generates executive-ready status reports, and proactively recommends actions to improve project execution.

## Architecture

```
User Request
     │
     ▼
┌─────────────┐
│  FastAPI     │
│  /api/project│
│  /analyze    │
└──────┬──────┘
       │
       ▼
┌──────────────────────────────────────────────┐
│           LangGraph Orchestrator             │
│                                              │
│  ┌──────────┐ ┌──────────┐ ┌──────────────┐ │
│  │  Sprint   │ │   Risk   │ │ Dependency   │ │  ← Phase 1 (parallel)
│  │  Agent    │ │  Agent   │ │   Agent      │ │
│  └────┬─────┘ └────┬─────┘ └──────┬───────┘ │
│       │             │              │         │
│       ▼             ▼              ▼         │
│  ┌──────────┐ ┌──────────────┐               │
│  │Forecasting│ │  Reporting   │               │  ← Phase 2 (depends on Phase 1)
│  │  Agent    │ │   Agent      │               │
│  └────┬─────┘ └──────┬───────┘               │
│       │               │                      │
│       └───────┬───────┘                      │
│               ▼                              │
│     ┌──────────────────┐                     │
│     │   Merge Results  │ → Health Report     │  ← Phase 3
│     └──────────────────┘                     │
└──────────────────────────────────────────────┘
```

### Agents

| Agent | Responsibility | Data Sources |
|---|---|---|
| Sprint Analysis | Track sprint progress, velocity, completion % | Jira |
| Risk Detection | Identify blockers, risks with evidence & impact | Jira, GitHub, Slack |
| Dependency Tracking | Detect dependency conflicts & critical path | Jira, GitHub |
| Stakeholder Reporting | Generate executive-ready status reports | All agent outputs |
| Delivery Forecasting | Predict sprint completion with confidence score | Jira, Sprint Agent |

### Tech Stack

| Layer | Technology |
|---|---|
| Orchestration | LangGraph (StateGraph with parallel fan-out) |
| LLM | OpenAI GPT-4o via LangChain |
| Backend | FastAPI (Python 3.12) |
| Frontend | React 18 + Vite |
| Integrations | Jira REST API, GitHub API, Slack API |
| Observability | LangSmith tracing |
| Infrastructure | Docker, Azure App Service / Static Web Apps |

## Project Structure

```
├── frontend/                   # React dashboard
│   ├── src/
│   │   ├── components/         # HealthScore, SprintCard, RiskCard, etc.
│   │   ├── App.jsx
│   │   └── main.jsx
│   ├── package.json
│   └── vite.config.js
├── backend/
│   ├── app/
│   │   ├── main.py             # FastAPI entry point
│   │   ├── api/                # Route handlers
│   │   ├── agents/             # 5 specialized LLM agents
│   │   ├── orchestrator/       # LangGraph workflow
│   │   ├── services/           # Jira, GitHub, Slack, Notes integrations
│   │   ├── models/             # Pydantic data schemas
│   │   └── utils/              # Structured logging
│   ├── requirements.txt
│   └── Dockerfile
├── infrastructure/
│   ├── azure/main.bicep
│   └── docker-compose.yml
├── .github/workflows/          # CI/CD pipelines
├── .env.example
└── README.md
```

## Setup

### Prerequisites

- Python 3.12+
- Node.js 20+
- API keys for: OpenAI, Jira, GitHub, Slack (optional), LangSmith (optional)

### 1. Clone & configure

```bash
git clone <repo-url>
cd Jira-sick-park
cp .env.example .env
# Edit .env with your actual API keys
```

### 2. Backend

```bash
cd backend
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # macOS/Linux
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Backend runs at `http://localhost:8000`. API docs at `/docs`.

### 3. Frontend

```bash
cd frontend
npm install
npm run dev
```

Frontend runs at `http://localhost:5173`, proxying API calls to the backend.

### 4. Docker (alternative)

```bash
cd infrastructure
docker-compose up --build
```

## API

### `POST /api/project/analyze`

Request:
```json
{
  "project_key": "PROJ",
  "sprint_id": "123",
  "github_repo": "org/repo",
  "slack_channel": "C0123456",
  "include_forecasting": true
}
```

Response: `ProjectHealthReport` with health score (0-100), sprint analysis, risks with evidence, dependencies, stakeholder report, and delivery forecast.

## Design Decisions

- **LangGraph over CrewAI**: Chose LangGraph for explicit control over the execution DAG, enabling true parallel fan-out in Phase 1 and deterministic merge in Phase 3.
- **Pydantic-enforced JSON**: Each agent outputs structured JSON validated by Pydantic models, ensuring type safety between agents.
- **Graceful degradation**: If any integration (Jira/GitHub/Slack) fails, the agent proceeds with available data rather than failing the entire pipeline.
- **Evidence-based scoring**: Health score is computed from concrete metrics (completion %, risk severity, conflict count, forecast confidence) — not LLM opinion.

## Known Limitations

- Historical velocity uses current sprint data only; multi-sprint historical analysis requires Jira board API access.
- Slack integration requires a bot token with `channels:history` scope.
- LangGraph fan-out edges run sequentially in the current LangGraph version; true async parallelism depends on the runtime.
- Meeting notes ingestion is file-based (markdown files in `meeting_notes/`); no transcription pipeline included.
=======
